import logging

from celery import shared_task
from celery.exceptions import SoftTimeLimitExceeded
from django.conf import settings
from django.utils import timezone

from detections.models import DetectionJob
from inference.service import InferenceService
from storage.backends import ObjectStorage

logger = logging.getLogger(__name__)


def execute_detection_job(job_id, *, inference_service=None, object_storage=None):
    service = inference_service or InferenceService()
    storage = object_storage or ObjectStorage()
    job = DetectionJob.objects.select_related("model").get(pk=job_id)
    if job.status in {DetectionJob.Status.CANCELLED, DetectionJob.Status.CANCEL_REQUESTED}:
        if job.status == DetectionJob.Status.CANCEL_REQUESTED:
            job.mark_cancelled()
        return "cancelled"
    if not job.mark_running():
        return job.status

    try:
        job.update_progress(10, "正在准备输入")
        with storage.materialize(job.asset_key) as local_path:
            job.refresh_from_db()
            if job.status == DetectionJob.Status.CANCEL_REQUESTED:
                job.mark_cancelled()
                return "cancelled"
            job.update_progress(35, "正在加载模型并识别")
            parameters = job.parameters or {}
            options = {
                "iou": float(parameters.get("iou", 0.5)),
                "conf": float(parameters.get("confidence", 0.45)),
            }
            if job.mode == DetectionJob.Mode.IMAGE:
                result = service.predict_image(job.model_id, str(local_path), **options)
            elif job.mode == DetectionJob.Mode.VIDEO:
                result = service.predict_video(job.model_id, str(local_path), **options)
            else:
                job.mark_failed("UNSUPPORTED_MODE", "该任务模式暂不支持异步处理。")
                return "failed"

        job.refresh_from_db()
        if job.status == DetectionJob.Status.CANCEL_REQUESTED:
            job.mark_cancelled()
            return "cancelled"
        job.update_progress(90, "正在整理识别结果")
        result.update(
            {
                "id": job.id,
                "mode": job.mode,
                "sourceName": job.original_filename,
                "model": job.model_snapshot,
                "dataKind": "real",
                "createdAt": timezone.now().isoformat(),
            }
        )
        return "succeeded" if job.mark_succeeded(result) else job.status
    except SoftTimeLimitExceeded:
        job.mark_timed_out("识别任务超过允许的处理时长。")
        return "timed_out"
    except Exception as exc:
        logger.exception(
            "Detection job failed",
            extra={"job_id": job.id, "error_type": type(exc).__name__},
        )
        job.mark_failed("INFERENCE_ERROR", "识别服务暂时不可用，请稍后重试。")
        return "failed"


@shared_task(
    bind=True,
    name="detections.process_detection_job",
    soft_time_limit=570,
    time_limit=600,
)
def process_detection_job(self, job_id):
    outcome = execute_detection_job(job_id)
    if outcome in {"failed", "timed_out"}:
        job = DetectionJob.objects.get(pk=job_id)
        if job.retry():
            raise self.retry(countdown=min(30 * (2 ** max(job.attempt_count - 1, 0)), 300))
    return outcome


def enqueue_detection_job(job_id):
    if getattr(settings, "CELERY_TASK_ALWAYS_EAGER", False):
        execute_detection_job(job_id)
        return f"eager:{job_id}"

    try:
        result = process_detection_job.apply_async(
            args=[job_id],
            queue=getattr(settings, "CELERY_DETECTION_QUEUE", "detections"),
            expires=getattr(settings, "CELERY_TASK_EXPIRES_SECONDS", 900),
        )
    except Exception as exc:
        logger.exception(
            "Detection queue dispatch failed",
            extra={"job_id": job_id, "error_type": type(exc).__name__},
        )
        job = DetectionJob.objects.get(pk=job_id)
        job.mark_dispatch_failed()
        return None
    DetectionJob.objects.filter(pk=job_id, status=DetectionJob.Status.QUEUED).update(
        celery_task_id=result.id,
        updated_at=timezone.now(),
    )
    return result.id

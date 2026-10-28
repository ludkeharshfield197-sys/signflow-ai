import re
from datetime import timedelta
from pathlib import PurePosixPath

from django.conf import settings
from django.db import transaction
from django.utils import timezone
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from api.authentication import SysUserJWTAuthentication
from api.response import error_response, success_response
from detections.models import DetectionJob
from detections.serializers import CreateDetectionJobSerializer, DetectionJobSerializer
from storage.backends import ObjectStorage, UploadValidationError


def safe_display_filename(name):
    basename = PurePosixPath(str(name).replace("\\", "/")).name
    return re.sub(r"[\x00-\x1f\x7f]", "", basename)[:255]


def schedule_detection_job(job):
    if not settings.DETECTION_AUTO_DISPATCH:
        return
    from detections.tasks import enqueue_detection_job

    transaction.on_commit(lambda: enqueue_detection_job(job.id))


class DetectionJobListCreateAPIView(APIView):
    authentication_classes = [SysUserJWTAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = CreateDetectionJobSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                request,
                "VALIDATION_ERROR",
                "识别任务参数不符合要求。",
                status=400,
                details=serializer.errors,
            )

        data = serializer.validated_data
        upload = data["file"]
        storage = ObjectStorage()
        try:
            stored = storage.save_upload(upload, owner_id=request.user.id, mode=data["mode"])
        except UploadValidationError as exc:
            return error_response(request, exc.code, str(exc), status=400)

        model = data["model"]
        try:
            with transaction.atomic():
                job = DetectionJob.objects.create(
                    owner=request.user,
                    mode=data["mode"],
                    asset_key=stored.key,
                    original_filename=safe_display_filename(upload.name),
                    content_type=stored.content_type,
                    size_bytes=stored.size,
                    input_sha256=stored.sha256,
                    model=model,
                    model_snapshot={
                        "id": model.id,
                        "name": model.name,
                        "version": model.version,
                        "fileSize": model.size,
                    },
                    preset=data["preset"],
                    parameters={
                        "iou": data["iou"],
                        "confidence": data["confidence"],
                    },
                    expires_at=timezone.now()
                    + timedelta(days=getattr(settings, "DETECTION_RETENTION_DAYS", 30)),
                )
        except Exception:
            storage.delete(stored.key)
            raise

        schedule_detection_job(job)
        return success_response(request, DetectionJobSerializer(job).data, status=201)


class DetectionJobDetailAPIView(APIView):
    authentication_classes = [SysUserJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, job_id):
        try:
            job = DetectionJob.objects.get(pk=job_id, owner=request.user)
        except DetectionJob.DoesNotExist:
            return error_response(request, "NOT_FOUND", "识别任务不存在。", status=404)
        return success_response(request, DetectionJobSerializer(job).data)


class DetectionJobCancelAPIView(APIView):
    authentication_classes = [SysUserJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, job_id):
        try:
            job = DetectionJob.objects.get(pk=job_id, owner=request.user)
        except DetectionJob.DoesNotExist:
            return error_response(request, "NOT_FOUND", "识别任务不存在。", status=404)
        if not job.request_cancel():
            return error_response(
                request,
                "INVALID_JOB_STATE",
                "当前任务状态无法取消。",
                status=409,
            )
        return success_response(request, DetectionJobSerializer(job).data)


class DetectionJobSaveAPIView(APIView):
    authentication_classes = [SysUserJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, job_id):
        try:
            job = DetectionJob.objects.get(pk=job_id, owner=request.user)
        except DetectionJob.DoesNotExist:
            return error_response(request, "NOT_FOUND", "识别任务不存在。", status=404)
        if job.status != DetectionJob.Status.SUCCEEDED:
            return error_response(
                request,
                "RESULT_NOT_READY",
                "识别完成后才能保存结果。",
                status=409,
            )
        if job.saved_at is None:
            job.mark_saved()
        data = dict(DetectionJobSerializer(job).data)
        data["saved"] = True
        return success_response(request, data)


class DetectionJobRetryAPIView(APIView):
    authentication_classes = [SysUserJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, job_id):
        try:
            job = DetectionJob.objects.get(pk=job_id, owner=request.user)
        except DetectionJob.DoesNotExist:
            return error_response(request, "NOT_FOUND", "识别任务不存在。", status=404)
        if not job.retry():
            return error_response(
                request,
                "RETRY_NOT_ALLOWED",
                "该任务已达到重试上限或当前状态不可重试。",
                status=409,
            )
        schedule_detection_job(job)
        return success_response(request, DetectionJobSerializer(job).data)

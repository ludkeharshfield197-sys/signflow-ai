from collections import Counter
from datetime import timedelta

from django.conf import settings
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Max, Q
from django.http import FileResponse
from django.utils import timezone
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from api.authentication import SysUserJWTAuthentication
from api.response import error_response, success_response
from detections.models import DetectionJob
from inference.model_profiles import get_model_profile
from modelYolo.models import YoloModel
from storage.backends import ObjectStorage

PRODUCT_DATA_SOURCE = "SignFlow AI \u5b9e\u9645\u8bc6\u522b\u4efb\u52a1"
TERMINAL_STATUSES = {
    DetectionJob.Status.SUCCEEDED,
    DetectionJob.Status.FAILED,
    DetectionJob.Status.TIMED_OUT,
    DetectionJob.Status.CANCELLED,
}
PENDING_STATUSES = {
    DetectionJob.Status.QUEUED,
    DetectionJob.Status.RUNNING,
    DetectionJob.Status.CANCEL_REQUESTED,
}


def _job_latency_ms(job):
    if not job.started_at or not job.completed_at:
        return None
    return max(int((job.completed_at - job.started_at).total_seconds() * 1000), 0)


def _success_rate(jobs):
    terminal_jobs = [job for job in jobs if job.status in TERMINAL_STATUSES]
    if not terminal_jobs:
        return 0
    succeeded = sum(job.status == DetectionJob.Status.SUCCEEDED for job in terminal_jobs)
    return round(succeeded / len(terminal_jobs) * 100, 1)


def _daily_series(jobs, days):
    today = timezone.localdate()
    series = []
    for offset in range(days - 1, -1, -1):
        target = today - timedelta(days=offset)
        daily_jobs = [job for job in jobs if timezone.localtime(job.created_at).date() == target]
        successful_latencies = [
            latency
            for job in daily_jobs
            if job.status == DetectionJob.Status.SUCCEEDED
            for latency in [_job_latency_ms(job)]
            if latency is not None
        ]
        series.append(
            {
                "date": target.strftime("%m-%d"),
                "tasks": len(daily_jobs),
                "latencyMs": (
                    round(sum(successful_latencies) / len(successful_latencies))
                    if successful_latencies
                    else 0
                ),
                "successRate": _success_rate(daily_jobs),
            }
        )
    return series


def result_payload(job):
    result = job.result or {}
    duration_ms = result.get("durationMs")
    if duration_ms is None and job.started_at and job.completed_at:
        duration_ms = max(int((job.completed_at - job.started_at).total_seconds() * 1000), 0)
    input_duration_ms = max(int(result.get("inputDurationMs") or duration_ms or 1), 1)
    raw_labels = result.get("labels") or []
    labels = []
    if raw_labels and isinstance(raw_labels[0], dict):
        labels = raw_labels
    elif raw_labels:
        segment = max(input_duration_ms // len(raw_labels), 1)
        labels = [
            {
                "text": str(label),
                "confidence": result.get("confidence"),
                "startMs": index * segment,
                "endMs": input_duration_ms
                if index == len(raw_labels) - 1
                else (index + 1) * segment,
            }
            for index, label in enumerate(raw_labels)
        ]
    model = {
        "id": job.model_snapshot.get("id", job.model_id),
        "name": job.model_snapshot.get("name", job.model.name),
        "version": job.model_snapshot.get("version", job.model.version),
    }
    confirmation_label = dict(DetectionJob.ConfirmationStatus.choices).get(
        job.confirmation_status,
        job.confirmation_status,
    )
    return {
        "id": job.id,
        "sentence": result.get("sentence") or "",
        "labels": labels,
        "confidence": result.get("confidence"),
        "durationMs": duration_ms or 0,
        "inputDurationMs": input_duration_ms,
        "model": model,
        "mode": job.mode,
        "sourceName": job.original_filename or "识别任务输入",
        "dataKind": "real",
        "status": job.status,
        "createdAt": job.created_at.isoformat(),
        "frames": result.get("frames"),
        "preset": job.preset,
        "advanced": job.parameters or {},
        "authorization": "任务所有者上传",
        "media": {
            "available": bool(job.asset_key),
            "contentType": job.content_type,
            "sizeBytes": job.size_bytes,
            "url": f"/api/v1/results/{job.id}/media/" if job.asset_key else "",
        },
        "trace": {
            "fileSha256": job.input_sha256,
            "modelSnapshot": job.model_snapshot or {},
            "parameters": job.parameters or {},
            "versionGroupId": str(job.version_group_id),
            "revision": job.revision,
            "parentResultId": job.parent_job_id,
        },
        "confirmation": {
            "status": job.confirmation_status,
            "label": confirmation_label,
            "confirmedAt": job.confirmed_at.isoformat() if job.confirmed_at else None,
            "confirmedBy": job.confirmed_by_id,
        },
        "revision": job.revision,
        "errorCode": job.error_code,
        "errorMessage": job.error_message,
    }


class ResultListAPIView(APIView):
    authentication_classes = [SysUserJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = DetectionJob.objects.filter(owner=request.user).select_related("model")
        mode = request.query_params.get("mode", "")
        status = request.query_params.get("status", "")
        query = request.query_params.get("query", "").strip()
        if mode and mode != "all":
            queryset = queryset.filter(mode=mode)
        if status and status != "all":
            queryset = queryset.filter(status=status)
        if query:
            queryset = queryset.filter(
                Q(id__icontains=query) | Q(original_filename__icontains=query)
            )
        try:
            page_number = max(int(request.query_params.get("page", 1)), 1)
            page_size = min(max(int(request.query_params.get("pageSize", 10)), 1), 100)
        except ValueError:
            return error_response(request, "VALIDATION_ERROR", "分页参数无效。", status=400)
        paginator = Paginator(queryset, page_size)
        page = paginator.get_page(page_number)
        return success_response(
            request,
            {
                "items": [result_payload(job) for job in page.object_list],
                "page": page.number,
                "pageSize": page_size,
                "total": paginator.count,
            },
        )


class ResultDetailAPIView(APIView):
    authentication_classes = [SysUserJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, result_id):
        try:
            job = DetectionJob.objects.select_related("model").get(pk=result_id, owner=request.user)
        except DetectionJob.DoesNotExist:
            return error_response(request, "NOT_FOUND", "识别结果不存在。", status=404)
        return success_response(request, result_payload(job))


class ResultMediaAPIView(APIView):
    authentication_classes = [SysUserJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, result_id):
        try:
            job = DetectionJob.objects.only(
                "asset_key",
                "content_type",
                "size_bytes",
                "original_filename",
            ).get(pk=result_id, owner=request.user)
        except DetectionJob.DoesNotExist:
            return error_response(request, "NOT_FOUND", "原始媒体不存在。", status=404)

        storage = ObjectStorage()
        if not job.asset_key or not storage.exists(job.asset_key):
            return error_response(request, "NOT_FOUND", "原始媒体已清理或不存在。", status=404)
        try:
            source = storage.open(job.asset_key)
        except (FileNotFoundError, OSError):
            return error_response(request, "NOT_FOUND", "原始媒体已清理或不存在。", status=404)

        response = FileResponse(
            source,
            content_type=job.content_type or "application/octet-stream",
        )
        if job.size_bytes:
            response["Content-Length"] = str(job.size_bytes)
        response["Content-Disposition"] = "inline"
        response["Cache-Control"] = "private, no-store"
        response["X-Content-Type-Options"] = "nosniff"
        return response


class ResultConfirmAPIView(APIView):
    authentication_classes = [SysUserJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, result_id):
        try:
            job = DetectionJob.objects.select_related("model").get(
                pk=result_id,
                owner=request.user,
            )
        except DetectionJob.DoesNotExist:
            return error_response(request, "NOT_FOUND", "识别结果不存在。", status=404)
        if job.confirmation_status != DetectionJob.ConfirmationStatus.BOTH_CONFIRMED:
            if not job.confirm_result(request.user):
                return error_response(
                    request,
                    "RESULT_NOT_READY",
                    "识别完成后才能确认结果。",
                    status=409,
                )
        return success_response(request, result_payload(job))


class ResultRerunAPIView(APIView):
    authentication_classes = [SysUserJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, result_id):
        storage = ObjectStorage()
        try:
            with transaction.atomic():
                source = (
                    DetectionJob.objects.select_for_update()
                    .select_related("model")
                    .get(pk=result_id, owner=request.user)
                )
                if source.status != DetectionJob.Status.SUCCEEDED:
                    return error_response(
                        request,
                        "RESULT_NOT_READY",
                        "识别完成后才能发起重新识别。",
                        status=409,
                    )
                if not source.asset_key or not storage.exists(source.asset_key):
                    return error_response(
                        request,
                        "SOURCE_MEDIA_UNAVAILABLE",
                        "原始媒体已清理，无法重新识别。",
                        status=410,
                    )
                latest_revision = (
                    DetectionJob.objects.filter(version_group_id=source.version_group_id)
                    .aggregate(latest=Max("revision"))
                    .get("latest")
                    or 1
                )
                replacement = DetectionJob.objects.create(
                    owner=source.owner,
                    mode=source.mode,
                    asset_key=source.asset_key,
                    original_filename=source.original_filename,
                    content_type=source.content_type,
                    size_bytes=source.size_bytes,
                    input_sha256=source.input_sha256,
                    model=source.model,
                    model_snapshot=source.model_snapshot,
                    preset=source.preset,
                    parameters=source.parameters,
                    version_group_id=source.version_group_id,
                    revision=latest_revision + 1,
                    parent_job=source,
                    expires_at=timezone.now()
                    + timedelta(days=getattr(settings, "DETECTION_RETENTION_DAYS", 30)),
                )
        except DetectionJob.DoesNotExist:
            return error_response(request, "NOT_FOUND", "识别结果不存在。", status=404)

        from detections.views import schedule_detection_job

        schedule_detection_job(replacement)
        return success_response(request, result_payload(replacement), status=201)


class ResultVersionsAPIView(APIView):
    authentication_classes = [SysUserJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, result_id):
        try:
            current = DetectionJob.objects.only("version_group_id").get(
                pk=result_id,
                owner=request.user,
            )
        except DetectionJob.DoesNotExist:
            return error_response(request, "NOT_FOUND", "识别结果不存在。", status=404)
        versions = (
            DetectionJob.objects.filter(
                owner=request.user,
                version_group_id=current.version_group_id,
            )
            .select_related("model")
            .order_by("revision", "created_at")
        )
        return success_response(
            request,
            {"items": [result_payload(job) for job in versions]},
        )


class OverviewAPIView(APIView):
    authentication_classes = [SysUserJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        jobs = list(
            DetectionJob.objects.filter(owner=request.user)
            .select_related("model")
            .order_by("-created_at")
        )
        today = timezone.localdate()
        today_jobs = [job for job in jobs if timezone.localtime(job.created_at).date() == today]
        today_succeeded = [job for job in today_jobs if job.status == DetectionJob.Status.SUCCEEDED]
        latencies = [
            latency
            for job in today_succeeded
            for latency in [_job_latency_ms(job)]
            if latency is not None
        ]
        recent_results = [
            result_payload(job) for job in jobs if job.status == DetectionJob.Status.SUCCEEDED
        ][:5]
        return success_response(
            request,
            {
                "source": PRODUCT_DATA_SOURCE,
                "serviceStatus": "api-only",
                "metrics": {
                    "completed": len(today_succeeded),
                    "pending": sum(job.status in PENDING_STATUSES for job in jobs),
                    "successRate": _success_rate(today_jobs),
                    "averageLatencyMs": (
                        round(sum(latencies) / len(latencies)) if latencies else None
                    ),
                },
                "recentResults": recent_results,
                "daily": _daily_series(jobs, 7),
                "updatedAt": timezone.now().isoformat(),
            },
        )


class AnalyticsAPIView(APIView):
    authentication_classes = [SysUserJWTAuthentication]
    permission_classes = [IsAuthenticated]

    RANGE_OPTIONS = {
        "7d": (7, "\u6700\u8fd1 7 \u5929"),
        "30d": (30, "\u6700\u8fd1 30 \u5929"),
        "90d": (90, "\u6700\u8fd1 90 \u5929"),
    }
    MODE_LABELS = {
        DetectionJob.Mode.IMAGE: "\u56fe\u7247",
        DetectionJob.Mode.VIDEO: "\u89c6\u9891",
        DetectionJob.Mode.LIVE: "\u5b9e\u65f6",
    }

    def get(self, request):
        range_key = request.query_params.get("range", "7d")
        if range_key not in self.RANGE_OPTIONS:
            return error_response(
                request,
                "VALIDATION_ERROR",
                "\u4ec5\u652f\u6301 7d\u300130d \u6216 90d \u7684\u5206\u6790\u8303\u56f4\u3002",
                status=400,
            )
        days, range_label = self.RANGE_OPTIONS[range_key]
        first_date = timezone.localdate() - timedelta(days=days - 1)
        jobs = [
            job
            for job in DetectionJob.objects.filter(owner=request.user).order_by("created_at")
            if timezone.localtime(job.created_at).date() >= first_date
        ]
        successful_latencies = [
            latency
            for job in jobs
            if job.status == DetectionJob.Status.SUCCEEDED
            for latency in [_job_latency_ms(job)]
            if latency is not None
        ]
        mode_counts = Counter(job.mode for job in jobs)
        label_counts = Counter()
        for job in jobs:
            for label in (job.result or {}).get("labels") or []:
                name = label.get("text") if isinstance(label, dict) else str(label)
                if name:
                    label_counts[name] += 1
        return success_response(
            request,
            {
                "range": range_label,
                "rangeKey": range_key,
                "source": PRODUCT_DATA_SOURCE,
                "metrics": {
                    "tasks": len(jobs),
                    "successRate": _success_rate(jobs),
                    "averageLatencyMs": (
                        round(sum(successful_latencies) / len(successful_latencies))
                        if successful_latencies
                        else None
                    ),
                },
                "daily": _daily_series(jobs, days),
                "modes": [
                    {"name": self.MODE_LABELS[mode], "value": mode_counts[mode]}
                    for mode in (
                        DetectionJob.Mode.IMAGE,
                        DetectionJob.Mode.VIDEO,
                        DetectionJob.Mode.LIVE,
                    )
                    if mode_counts[mode]
                ],
                "popularLabels": [
                    {"name": name, "value": value} for name, value in label_counts.most_common(10)
                ],
                "updatedAt": timezone.now().isoformat(),
            },
        )


def model_payload(model):
    profile = get_model_profile(model.file_path) or {}
    evaluation = model.evaluation or {}
    metrics = evaluation.get("metrics") or {}
    dataset = evaluation.get("dataset") or {}
    map50 = metrics.get("map50")
    latest_job = model.detection_jobs.order_by("-created_at").only("created_at").first()
    status_text = str(model.status)
    is_ready = status_text.lower() in {"正常", "active", "deployed", "ready"}
    return {
        "id": model.id,
        "name": model.name,
        "version": model.version,
        "classes": profile.get("classCount"),
        "language": profile.get("language"),
        "languageCode": profile.get("languageCode"),
        "fileSize": model.size,
        "status": "active" if is_ready else "inactive",
        "statusLabel": "可用" if is_ready else status_text,
        "lastUsedAt": latest_job.created_at.isoformat() if latest_job else None,
        "metric": {
            "value": f"{float(map50) * 100:.1f}%" if isinstance(map50, (int, float)) else None,
            "name": "验证集 mAP50",
            "source": evaluation.get("source")
            or ("本地 YOLO.val 复测" if evaluation.get("status") == "evaluated" else ""),
            "dataset": dataset.get("name", ""),
            "sampleCount": dataset.get("sampleCount"),
            "evaluatedAt": evaluation.get("evaluatedAt", ""),
        },
        "evaluation": evaluation,
        "deployment": getattr(settings, "MODEL_DEPLOYMENT_LABEL", "异步推理服务"),
        "description": model.remark or "暂无模型说明",
    }


class ModelCatalogAPIView(APIView):
    authentication_classes = [SysUserJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        models = YoloModel.objects.all().order_by("-upload_time", "-id")
        return success_response(request, {"items": [model_payload(model) for model in models]})


class PublicModelMetricsAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        model = (
            YoloModel.objects.filter(status__in=["正常", "active", "deployed", "ready"])
            .order_by(
                "-upload_time",
                "-id",
            )
            .first()
        )
        if model is None:
            return error_response(
                request, "METRICS_UNAVAILABLE", "当前未连接评测服务。", status=503
            )
        return success_response(
            request,
            {
                "version": model.version,
                "dataset": (model.evaluation or {}).get("dataset", {}).get("name")
                or getattr(settings, "MODEL_EVALUATION_DATASET", "")
                or "未配置",
                "sampleCount": (model.evaluation or {}).get("dataset", {}).get("sampleCount")
                or getattr(settings, "MODEL_EVALUATION_SAMPLE_COUNT", "")
                or "—",
                "evaluatedAt": (model.evaluation or {}).get("evaluatedAt")
                or getattr(settings, "MODEL_EVALUATED_AT", "")
                or "—",
            },
        )

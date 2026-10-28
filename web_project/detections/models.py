import uuid

from django.db import models, transaction
from django.utils import timezone

from modelYolo.models import YoloModel
from user.models import SysUser


def generate_detection_id():
    return f"det_{uuid.uuid4().hex[:24]}"


class DetectionJob(models.Model):
    class Mode(models.TextChoices):
        IMAGE = "image", "图片"
        VIDEO = "video", "视频"
        LIVE = "live", "实时"

    class Status(models.TextChoices):
        QUEUED = "queued", "排队中"
        RUNNING = "running", "处理中"
        SUCCEEDED = "succeeded", "已完成"
        FAILED = "failed", "失败"
        CANCEL_REQUESTED = "cancel_requested", "正在取消"
        CANCELLED = "cancelled", "已取消"
        TIMED_OUT = "timed_out", "已超时"

    class ConfirmationStatus(models.TextChoices):
        PENDING = "pending", "待确认"
        BOTH_CONFIRMED = "both_confirmed", "双方已确认"
        DISPUTED = "disputed", "结果存疑"

    id = models.CharField(
        primary_key=True, max_length=32, default=generate_detection_id, editable=False
    )
    owner = models.ForeignKey(SysUser, on_delete=models.PROTECT, related_name="detection_jobs")
    mode = models.CharField(max_length=12, choices=Mode.choices)
    asset_key = models.CharField(max_length=512)
    original_filename = models.CharField(max_length=255, blank=True, default="")
    content_type = models.CharField(max_length=120, blank=True, default="")
    size_bytes = models.PositiveBigIntegerField(default=0)
    input_sha256 = models.CharField(max_length=64, blank=True, default="")
    model = models.ForeignKey(YoloModel, on_delete=models.PROTECT, related_name="detection_jobs")
    model_snapshot = models.JSONField(default=dict)
    preset = models.CharField(max_length=32, default="balanced")
    parameters = models.JSONField(default=dict)
    status = models.CharField(max_length=24, choices=Status.choices, default=Status.QUEUED)
    progress = models.PositiveSmallIntegerField(default=0)
    stage_label = models.CharField(max_length=120, blank=True, default="等待处理")
    result = models.JSONField(null=True, blank=True)
    result_asset_key = models.CharField(max_length=512, blank=True, default="")
    error_code = models.CharField(max_length=64, blank=True, default="")
    error_message = models.TextField(blank=True, default="")
    attempt_count = models.PositiveSmallIntegerField(default=0)
    max_attempts = models.PositiveSmallIntegerField(default=3)
    celery_task_id = models.CharField(max_length=255, blank=True, default="")
    queued_at = models.DateTimeField(default=timezone.now)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    saved_at = models.DateTimeField(null=True, blank=True)
    confirmation_status = models.CharField(
        max_length=24,
        choices=ConfirmationStatus.choices,
        default=ConfirmationStatus.PENDING,
    )
    confirmed_at = models.DateTimeField(null=True, blank=True)
    confirmed_by = models.ForeignKey(
        SysUser,
        on_delete=models.PROTECT,
        related_name="confirmed_detection_jobs",
        null=True,
        blank=True,
    )
    version_group_id = models.UUIDField(default=uuid.uuid4, editable=False, db_index=True)
    revision = models.PositiveIntegerField(default=1)
    parent_job = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        related_name="child_revisions",
        null=True,
        blank=True,
    )
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "detection_job"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["version_group_id", "revision"],
                name="detection_unique_version_revision",
            )
        ]

    def _transition(
        self,
        *,
        allowed_statuses,
        event_type,
        mutate,
        guard=None,
        metadata=None,
    ):
        with transaction.atomic():
            current = type(self).objects.select_for_update().get(pk=self.pk)
            if current.status not in allowed_statuses or (guard and not guard(current)):
                accepted = False
            else:
                from_status = current.status
                resolved_event = event_type(current) if callable(event_type) else event_type
                mutate(current)
                current.save()
                DetectionJobEvent.objects.create(
                    job=current,
                    event_type=resolved_event,
                    from_status=from_status,
                    to_status=current.status,
                    metadata=metadata or {},
                )
                accepted = True
        self.refresh_from_db()
        return accepted

    def mark_running(self):
        now = timezone.now()

        def mutate(current):
            current.status = self.Status.RUNNING
            current.progress = 1
            current.stage_label = "任务正在处理"
            current.attempt_count += 1
            current.started_at = now

        return self._transition(
            allowed_statuses=[self.Status.QUEUED],
            event_type="started",
            mutate=mutate,
        )

    def mark_failed(self, error_code, error_message):
        now = timezone.now()

        def mutate(current):
            current.status = self.Status.FAILED
            current.error_code = error_code
            current.error_message = error_message
            current.completed_at = now

        return self._transition(
            allowed_statuses=[self.Status.RUNNING],
            event_type="failed",
            mutate=mutate,
            metadata={"errorCode": error_code},
        )

    def mark_dispatch_failed(self):
        now = timezone.now()

        def mutate(current):
            current.status = self.Status.FAILED
            current.error_code = "QUEUE_UNAVAILABLE"
            current.error_message = "任务队列暂时不可用，请稍后重试。"
            current.completed_at = now

        return self._transition(
            allowed_statuses=[self.Status.QUEUED],
            event_type="dispatch_failed",
            mutate=mutate,
            metadata={"errorCode": "QUEUE_UNAVAILABLE"},
        )

    def mark_timed_out(self, error_message):
        now = timezone.now()

        def mutate(current):
            current.status = self.Status.TIMED_OUT
            current.error_code = "TASK_TIMEOUT"
            current.error_message = error_message
            current.completed_at = now

        return self._transition(
            allowed_statuses=[self.Status.RUNNING],
            event_type="timed_out",
            mutate=mutate,
            metadata={"errorCode": "TASK_TIMEOUT"},
        )

    def retry(self):
        def mutate(current):
            current.status = self.Status.QUEUED
            current.progress = 0
            current.stage_label = "等待重试"
            current.result = None
            current.error_code = ""
            current.error_message = ""
            current.started_at = None
            current.completed_at = None

        return self._transition(
            allowed_statuses=[self.Status.FAILED, self.Status.TIMED_OUT],
            event_type="retried",
            mutate=mutate,
            guard=lambda current: current.attempt_count < current.max_attempts,
        )

    def mark_succeeded(self, result):
        now = timezone.now()

        def mutate(current):
            current.status = self.Status.SUCCEEDED
            current.progress = 100
            current.stage_label = "识别完成"
            current.result = result
            current.completed_at = now

        return self._transition(
            allowed_statuses=[self.Status.RUNNING],
            event_type="succeeded",
            mutate=mutate,
        )

    def update_progress(self, progress, stage_label):
        bounded_progress = min(max(int(progress), 1), 99)

        def mutate(current):
            current.progress = bounded_progress
            current.stage_label = stage_label

        return self._transition(
            allowed_statuses=[self.Status.RUNNING],
            event_type="progress",
            mutate=mutate,
            guard=lambda current: current.progress < bounded_progress,
            metadata={"progress": bounded_progress, "stageLabel": stage_label},
        )

    def request_cancel(self):
        now = timezone.now()

        def event_type(current):
            return "cancelled" if current.status == self.Status.QUEUED else "cancel_requested"

        def mutate(current):
            if current.status == self.Status.QUEUED:
                current.status = self.Status.CANCELLED
                current.cancelled_at = now
                current.completed_at = now
                current.stage_label = "任务已取消"
            else:
                current.status = self.Status.CANCEL_REQUESTED
                current.stage_label = "正在取消"

        return self._transition(
            allowed_statuses=[self.Status.QUEUED, self.Status.RUNNING],
            event_type=event_type,
            mutate=mutate,
        )

    def mark_cancelled(self):
        now = timezone.now()

        def mutate(current):
            current.status = self.Status.CANCELLED
            current.cancelled_at = now
            current.completed_at = now
            current.stage_label = "任务已取消"

        return self._transition(
            allowed_statuses=[
                self.Status.RUNNING,
                self.Status.CANCEL_REQUESTED,
                self.Status.QUEUED,
            ],
            event_type="cancelled",
            mutate=mutate,
        )

    def mark_saved(self):
        now = timezone.now()

        def mutate(current):
            current.saved_at = now

        return self._transition(
            allowed_statuses=[self.Status.SUCCEEDED],
            event_type="saved",
            mutate=mutate,
            guard=lambda current: current.saved_at is None,
        )

    def confirm_result(self, user):
        now = timezone.now()

        def mutate(current):
            current.confirmation_status = self.ConfirmationStatus.BOTH_CONFIRMED
            current.confirmed_at = now
            current.confirmed_by = user

        if self.confirmation_status == self.ConfirmationStatus.BOTH_CONFIRMED:
            return True
        return self._transition(
            allowed_statuses=[self.Status.SUCCEEDED],
            event_type="result_confirmed",
            mutate=mutate,
            guard=lambda current: (
                current.confirmation_status != self.ConfirmationStatus.BOTH_CONFIRMED
            ),
            metadata={"confirmedBy": user.id},
        )


class DetectionJobEvent(models.Model):
    job = models.ForeignKey(DetectionJob, on_delete=models.CASCADE, related_name="events")
    event_type = models.CharField(max_length=32)
    from_status = models.CharField(max_length=24, blank=True, default="")
    to_status = models.CharField(max_length=24)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "detection_job_event"
        ordering = ["created_at", "id"]

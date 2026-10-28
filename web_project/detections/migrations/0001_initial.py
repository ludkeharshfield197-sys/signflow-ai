from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import detections.models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("modelYolo", "0002_yolomodel_creator"),
        ("user", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="DetectionJob",
            fields=[
                (
                    "id",
                    models.CharField(
                        default=detections.models.generate_detection_id,
                        editable=False,
                        max_length=32,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "mode",
                    models.CharField(
                        choices=[("image", "图片"), ("video", "视频"), ("live", "实时")],
                        max_length=12,
                    ),
                ),
                ("asset_key", models.CharField(max_length=512)),
                ("original_filename", models.CharField(blank=True, default="", max_length=255)),
                ("content_type", models.CharField(blank=True, default="", max_length=120)),
                ("size_bytes", models.PositiveBigIntegerField(default=0)),
                ("model_snapshot", models.JSONField(default=dict)),
                ("preset", models.CharField(default="balanced", max_length=32)),
                ("parameters", models.JSONField(default=dict)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("queued", "排队中"),
                            ("running", "处理中"),
                            ("succeeded", "已完成"),
                            ("failed", "失败"),
                            ("cancel_requested", "正在取消"),
                            ("cancelled", "已取消"),
                            ("timed_out", "已超时"),
                        ],
                        default="queued",
                        max_length=24,
                    ),
                ),
                ("progress", models.PositiveSmallIntegerField(default=0)),
                ("stage_label", models.CharField(blank=True, default="等待处理", max_length=120)),
                ("result", models.JSONField(blank=True, null=True)),
                ("result_asset_key", models.CharField(blank=True, default="", max_length=512)),
                ("error_code", models.CharField(blank=True, default="", max_length=64)),
                ("error_message", models.TextField(blank=True, default="")),
                ("attempt_count", models.PositiveSmallIntegerField(default=0)),
                ("max_attempts", models.PositiveSmallIntegerField(default=3)),
                ("celery_task_id", models.CharField(blank=True, default="", max_length=255)),
                ("queued_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("started_at", models.DateTimeField(blank=True, null=True)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                ("cancelled_at", models.DateTimeField(blank=True, null=True)),
                ("saved_at", models.DateTimeField(blank=True, null=True)),
                ("expires_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "model",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="detection_jobs",
                        to="modelYolo.yolomodel",
                    ),
                ),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="detection_jobs",
                        to="user.sysuser",
                    ),
                ),
            ],
            options={"db_table": "detection_job", "ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="DetectionJobEvent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("event_type", models.CharField(max_length=32)),
                ("from_status", models.CharField(blank=True, default="", max_length=24)),
                ("to_status", models.CharField(max_length=24)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "job",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="events",
                        to="detections.detectionjob",
                    ),
                ),
            ],
            options={"db_table": "detection_job_event", "ordering": ["created_at", "id"]},
        ),
    ]

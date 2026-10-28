import uuid

import django.db.models.deletion
from django.db import migrations, models


def assign_version_groups(apps, schema_editor):
    DetectionJob = apps.get_model("detections", "DetectionJob")
    for job in DetectionJob.objects.filter(version_group_id__isnull=True).iterator():
        job.version_group_id = uuid.uuid4()
        job.save(update_fields=["version_group_id"])


class Migration(migrations.Migration):
    dependencies = [
        ("detections", "0001_initial"),
        ("user", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="detectionjob",
            name="input_sha256",
            field=models.CharField(blank=True, default="", max_length=64),
        ),
        migrations.AddField(
            model_name="detectionjob",
            name="confirmation_status",
            field=models.CharField(
                choices=[
                    ("pending", "待确认"),
                    ("both_confirmed", "双方已确认"),
                    ("disputed", "结果存疑"),
                ],
                default="pending",
                max_length=24,
            ),
        ),
        migrations.AddField(
            model_name="detectionjob",
            name="confirmed_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="detectionjob",
            name="confirmed_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="confirmed_detection_jobs",
                to="user.sysuser",
            ),
        ),
        migrations.AddField(
            model_name="detectionjob",
            name="parent_job",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="child_revisions",
                to="detections.detectionjob",
            ),
        ),
        migrations.AddField(
            model_name="detectionjob",
            name="revision",
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AddField(
            model_name="detectionjob",
            name="version_group_id",
            field=models.UUIDField(db_index=True, editable=False, null=True),
        ),
        migrations.RunPython(assign_version_groups, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="detectionjob",
            name="version_group_id",
            field=models.UUIDField(db_index=True, default=uuid.uuid4, editable=False),
        ),
        migrations.AddConstraint(
            model_name="detectionjob",
            constraint=models.UniqueConstraint(
                fields=("version_group_id", "revision"),
                name="detection_unique_version_revision",
            ),
        ),
    ]

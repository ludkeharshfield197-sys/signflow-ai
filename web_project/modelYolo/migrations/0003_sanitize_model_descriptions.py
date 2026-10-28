from django.db import migrations

FORBIDDEN_MARKERS = ("比赛", "竞赛", "参赛", "competition", "demonstration")
NEUTRAL_DESCRIPTION = "本地多类别手语识别模型"


def sanitize_model_descriptions(apps, schema_editor):
    yolo_model = apps.get_model("modelYolo", "YoloModel")
    for model in yolo_model.objects.exclude(remark__isnull=True).iterator():
        description = model.remark or ""
        if any(marker in description.lower() for marker in FORBIDDEN_MARKERS):
            model.remark = NEUTRAL_DESCRIPTION
            model.save(update_fields=["remark"])


class Migration(migrations.Migration):
    dependencies = [
        ("modelYolo", "0002_yolomodel_creator"),
    ]

    operations = [
        migrations.RunPython(sanitize_model_descriptions, migrations.RunPython.noop),
    ]

from django.db import migrations, models


def normalize_model_descriptions(apps, schema_editor):
    yolo_model = apps.get_model("modelYolo", "YoloModel")
    yolo_model.objects.all().update(remark="本地多类别手语识别模型")


class Migration(migrations.Migration):
    dependencies = [
        ("modelYolo", "0003_sanitize_model_descriptions"),
    ]

    operations = [
        migrations.AddField(
            model_name="yolomodel",
            name="evaluation",
            field=models.JSONField(blank=True, default=dict, verbose_name="评测卡"),
        ),
        migrations.RunPython(normalize_model_descriptions, migrations.RunPython.noop),
    ]

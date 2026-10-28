from rest_framework import serializers

from detections.models import DetectionJob
from modelYolo.models import YoloModel


class CreateDetectionJobSerializer(serializers.Serializer):
    mode = serializers.ChoiceField(choices=["image", "video"])
    modelId = serializers.PrimaryKeyRelatedField(
        queryset=YoloModel.objects.all(),
        source="model",
    )
    preset = serializers.ChoiceField(
        choices=["fast", "balanced", "precise"],
        default="balanced",
    )
    iou = serializers.FloatField(min_value=0.05, max_value=0.95, default=0.5)
    confidence = serializers.FloatField(min_value=0.05, max_value=0.99, default=0.45)
    file = serializers.FileField()

    def validate_modelId(self, model):
        if str(model.status).lower() not in {"正常", "active", "deployed", "ready"}:
            raise serializers.ValidationError("所选模型当前不可用于识别。")
        return model


class DetectionJobSerializer(serializers.ModelSerializer):
    result = serializers.SerializerMethodField()
    stageLabel = serializers.CharField(source="stage_label", read_only=True)
    errorMessage = serializers.CharField(source="error_message", read_only=True)
    errorCode = serializers.CharField(source="error_code", read_only=True)
    modelSnapshot = serializers.JSONField(source="model_snapshot", read_only=True)
    createdAt = serializers.DateTimeField(source="created_at", read_only=True)
    completedAt = serializers.DateTimeField(source="completed_at", read_only=True)

    def get_result(self, job):
        if not job.result:
            return None
        from api.product_views import result_payload

        return result_payload(job)

    class Meta:
        model = DetectionJob
        fields = (
            "id",
            "mode",
            "status",
            "progress",
            "stageLabel",
            "result",
            "errorCode",
            "errorMessage",
            "modelSnapshot",
            "createdAt",
            "completedAt",
        )
        read_only_fields = fields

from io import BytesIO

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from rest_framework.test import APIClient

from modelYolo.models import YoloModel
from user.models import SysUser


def valid_jpeg_upload(name="gesture.jpg"):
    buffer = BytesIO()
    Image.new("RGB", (8, 8), color=(42, 38, 97)).save(buffer, format="JPEG")
    return SimpleUploadedFile(name, buffer.getvalue(), content_type="image/jpeg")


@pytest.mark.django_db
def test_create_detection_job_owns_the_asset_and_freezes_the_model_snapshot(settings, tmp_path):
    from detections.models import DetectionJob

    settings.MEDIA_ROOT = tmp_path / "media"
    owner = SysUser.objects.create(username="api_job_owner", password="unused", status=0)
    model = YoloModel.objects.create(
        name="SignFlow API Test",
        version="2.1-test",
        size="1 MB",
        status="正常",
        file_path="signflow-test.pt",
        creator=owner,
    )
    client = APIClient()
    client.force_authenticate(user=owner)

    response = client.post(
        "/api/v1/detections/jobs/",
        {
            "mode": "image",
            "modelId": model.id,
            "preset": "balanced",
            "iou": "0.50",
            "confidence": "0.45",
            "file": valid_jpeg_upload("../../private-gesture.jpg"),
        },
        format="multipart",
    )

    assert response.status_code == 201
    assert response.data["success"] is True
    assert response.data["data"]["status"] == "queued"
    job = DetectionJob.objects.get(pk=response.data["data"]["id"])
    assert job.owner == owner
    assert job.asset_key.startswith(f"users/{owner.id}/detections/")
    assert "private-gesture" not in job.asset_key
    assert job.model_snapshot == {
        "id": model.id,
        "name": model.name,
        "version": model.version,
        "fileSize": model.size,
    }
    assert job.parameters == {"iou": 0.5, "confidence": 0.45}


@pytest.mark.django_db
def test_detection_job_detail_is_visible_only_to_its_owner():
    from detections.models import DetectionJob

    owner = SysUser.objects.create(username="detail_owner", password="unused", status=0)
    stranger = SysUser.objects.create(username="detail_stranger", password="unused", status=0)
    model = YoloModel.objects.create(
        name="SignFlow Detail Test",
        version="2.1-test",
        size="1 MB",
        status="正常",
        file_path="signflow-test.pt",
        creator=owner,
    )
    job = DetectionJob.objects.create(
        owner=owner,
        mode="image",
        asset_key=f"users/{owner.id}/detections/private.jpg",
        model=model,
        model_snapshot={"id": model.id, "version": model.version},
    )
    client = APIClient()
    client.force_authenticate(user=owner)
    owner_response = client.get(f"/api/v1/detections/jobs/{job.id}/")
    client.force_authenticate(user=stranger)
    stranger_response = client.get(f"/api/v1/detections/jobs/{job.id}/")

    assert owner_response.status_code == 200
    assert owner_response.data["data"]["id"] == job.id
    assert "asset_key" not in owner_response.data["data"]
    assert stranger_response.status_code == 404
    assert stranger_response.data["error"]["code"] == "NOT_FOUND"


@pytest.mark.django_db
def test_completed_detection_job_detail_returns_a_presentation_ready_result():
    from detections.models import DetectionJob

    owner = SysUser.objects.create(username="result_shape_owner", password="unused", status=0)
    model = YoloModel.objects.create(
        name="SignFlow Result Shape Test",
        version="2.1-test",
        size="1 MB",
        status="正常",
        file_path="signflow-test.pt",
        creator=owner,
    )
    job = DetectionJob.objects.create(
        owner=owner,
        mode="image",
        asset_key=f"users/{owner.id}/detections/milk.jpg",
        original_filename="milk.jpg",
        model=model,
        model_snapshot={"id": model.id, "name": model.name, "version": model.version},
    )
    job.mark_running()
    job.mark_succeeded(
        {
            "sentence": "milk",
            "labels": ["milk"],
            "confidence": 0.655,
            "detections": [{"label": "milk", "confidence": 0.655}],
        }
    )
    client = APIClient()
    client.force_authenticate(user=owner)

    response = client.get(f"/api/v1/detections/jobs/{job.id}/")

    assert response.status_code == 200
    result = response.data["data"]["result"]
    assert result["labels"] == [
        {
            "text": "milk",
            "confidence": 0.655,
            "startMs": 0,
            "endMs": result["inputDurationMs"],
        }
    ]
    assert isinstance(result["durationMs"], int)
    assert result["durationMs"] >= 0
    assert result["model"] == {
        "id": model.id,
        "name": model.name,
        "version": model.version,
    }


@pytest.mark.django_db
def test_owner_can_request_cancellation_of_a_running_job():
    from detections.models import DetectionJob

    owner = SysUser.objects.create(username="cancel_api_owner", password="unused", status=0)
    model = YoloModel.objects.create(
        name="SignFlow Cancel API Test",
        version="2.1-test",
        size="1 MB",
        status="正常",
        file_path="signflow-test.pt",
        creator=owner,
    )
    job = DetectionJob.objects.create(
        owner=owner,
        mode="video",
        asset_key=f"users/{owner.id}/detections/input.mp4",
        model=model,
        model_snapshot={"id": model.id, "version": model.version},
    )
    job.mark_running()
    client = APIClient()
    client.force_authenticate(user=owner)

    response = client.post(f"/api/v1/detections/jobs/{job.id}/cancel/", {}, format="json")

    assert response.status_code == 200
    assert response.data["data"]["status"] == "cancel_requested"
    job.refresh_from_db()
    assert job.status == "cancel_requested"


@pytest.mark.django_db
def test_owner_can_save_only_a_completed_result():
    from detections.models import DetectionJob

    owner = SysUser.objects.create(username="save_api_owner", password="unused", status=0)
    model = YoloModel.objects.create(
        name="SignFlow Save API Test",
        version="2.1-test",
        size="1 MB",
        status="正常",
        file_path="signflow-test.pt",
        creator=owner,
    )
    job = DetectionJob.objects.create(
        owner=owner,
        mode="image",
        asset_key=f"users/{owner.id}/detections/input.jpg",
        model=model,
        model_snapshot={"id": model.id, "version": model.version},
    )
    job.mark_running()
    job.mark_succeeded({"sentence": "你好", "detections": []})
    client = APIClient()
    client.force_authenticate(user=owner)

    response = client.post(f"/api/v1/detections/jobs/{job.id}/save/", {}, format="json")

    assert response.status_code == 200
    assert response.data["data"]["saved"] is True
    job.refresh_from_db()
    assert job.saved_at is not None


@pytest.mark.django_db
def test_owner_can_retry_a_failed_job_with_the_same_asset_and_snapshot():
    from detections.models import DetectionJob

    owner = SysUser.objects.create(username="retry_api_owner", password="unused", status=0)
    model = YoloModel.objects.create(
        name="SignFlow Retry API Test",
        version="2.1-test",
        size="1 MB",
        status="正常",
        file_path="signflow-test.pt",
        creator=owner,
    )
    job = DetectionJob.objects.create(
        owner=owner,
        mode="image",
        asset_key=f"users/{owner.id}/detections/input.jpg",
        model=model,
        model_snapshot={"id": model.id, "version": model.version},
    )
    job.mark_running()
    job.mark_failed("INFERENCE_ERROR", "模型服务暂时不可用")
    client = APIClient()
    client.force_authenticate(user=owner)

    response = client.post(f"/api/v1/detections/jobs/{job.id}/retry/", {}, format="json")

    assert response.status_code == 200
    assert response.data["data"]["status"] == "queued"
    job.refresh_from_db()
    assert job.asset_key.endswith("input.jpg")
    assert job.model_snapshot["version"] == "2.1-test"

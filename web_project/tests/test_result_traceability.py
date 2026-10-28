import hashlib
from io import BytesIO

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from rest_framework.test import APIClient

from detections.models import DetectionJob
from modelYolo.models import YoloModel
from user.models import SysUser


def jpeg_bytes():
    buffer = BytesIO()
    Image.new("RGB", (12, 8), color=(42, 38, 97)).save(buffer, format="JPEG")
    return buffer.getvalue()


def create_owner_and_model(username):
    owner = SysUser.objects.create(username=username, password="unused", status=0)
    model = YoloModel.objects.create(
        name="SignFlow Traceability Test",
        version="2.1-test",
        size="1 MB",
        status="正常",
        file_path="signflow-test.pt",
        creator=owner,
    )
    return owner, model


def upload_job(client, model, content):
    return client.post(
        "/api/v1/detections/jobs/",
        {
            "mode": "image",
            "modelId": model.id,
            "preset": "balanced",
            "iou": "0.50",
            "confidence": "0.45",
            "file": SimpleUploadedFile("gesture.jpg", content, content_type="image/jpeg"),
        },
        format="multipart",
    )


@pytest.mark.django_db
def test_uploaded_media_sha256_is_persisted_and_exposed_without_leaking_storage_key(
    settings, tmp_path
):
    settings.MEDIA_ROOT = tmp_path / "media"
    owner, model = create_owner_and_model("trace_hash_owner")
    client = APIClient()
    client.force_authenticate(user=owner)
    content = jpeg_bytes()

    response = upload_job(client, model, content)

    assert response.status_code == 201
    job = DetectionJob.objects.get(pk=response.data["data"]["id"])
    assert job.input_sha256 == hashlib.sha256(content).hexdigest()
    detail = client.get(f"/api/v1/results/{job.id}/")
    assert detail.data["data"]["trace"]["fileSha256"] == job.input_sha256
    assert detail.data["data"]["trace"]["modelSnapshot"]["version"] == "2.1-test"
    assert detail.data["data"]["trace"]["parameters"] == {
        "iou": 0.5,
        "confidence": 0.45,
    }
    assert "asset_key" not in str(detail.data)


@pytest.mark.django_db
def test_original_media_is_streamed_only_to_the_task_owner(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path / "media"
    owner, model = create_owner_and_model("trace_media_owner")
    stranger = SysUser.objects.create(username="trace_media_stranger", password="unused", status=0)
    owner_client = APIClient()
    owner_client.force_authenticate(user=owner)
    content = jpeg_bytes()
    created = upload_job(owner_client, model, content)
    job_id = created.data["data"]["id"]

    owner_response = owner_client.get(f"/api/v1/results/{job_id}/media/")
    owner_body = b"".join(owner_response.streaming_content)
    stranger_client = APIClient()
    stranger_client.force_authenticate(user=stranger)
    stranger_response = stranger_client.get(f"/api/v1/results/{job_id}/media/")

    assert owner_response.status_code == 200
    assert owner_response["Content-Type"] == "image/jpeg"
    assert owner_response["Cache-Control"] == "private, no-store"
    assert owner_response["X-Content-Type-Options"] == "nosniff"
    assert owner_body == content
    assert stranger_response.status_code == 404


@pytest.mark.django_db
def test_confirmation_is_persisted_as_both_confirmed_and_is_idempotent():
    owner, model = create_owner_and_model("trace_confirm_owner")
    job = DetectionJob.objects.create(
        owner=owner,
        mode="image",
        asset_key=f"users/{owner.id}/detections/input.jpg",
        original_filename="gesture.jpg",
        content_type="image/jpeg",
        input_sha256="a" * 64,
        model=model,
        model_snapshot={"id": model.id, "name": model.name, "version": model.version},
        parameters={"iou": 0.5, "confidence": 0.45},
    )
    job.mark_running()
    job.mark_succeeded({"sentence": "你好", "confidence": 0.95, "labels": []})
    client = APIClient()
    client.force_authenticate(user=owner)

    first = client.post(f"/api/v1/results/{job.id}/confirm/", {}, format="json")
    second = client.post(f"/api/v1/results/{job.id}/confirm/", {}, format="json")
    detail = client.get(f"/api/v1/results/{job.id}/")

    assert first.status_code == 200
    assert second.status_code == 200
    assert detail.data["data"]["confirmation"]["status"] == "both_confirmed"
    assert detail.data["data"]["confirmation"]["label"] == "双方已确认"
    assert detail.data["data"]["confirmation"]["confirmedAt"]
    job.refresh_from_db()
    assert job.confirmed_by == owner
    assert job.confirmed_at is not None


@pytest.mark.django_db
def test_rerecognition_creates_an_immutable_revision_and_versions_can_be_compared(
    settings, tmp_path
):
    settings.MEDIA_ROOT = tmp_path / "media"
    owner, model = create_owner_and_model("trace_revision_owner")
    client = APIClient()
    client.force_authenticate(user=owner)
    created = upload_job(client, model, jpeg_bytes())
    original = DetectionJob.objects.get(pk=created.data["data"]["id"])
    original.mark_running()
    original.mark_succeeded({"sentence": "你好", "confidence": 0.95, "labels": []})

    rerun = client.post(f"/api/v1/results/{original.id}/rerun/", {}, format="json")

    assert rerun.status_code == 201
    replacement = DetectionJob.objects.get(pk=rerun.data["data"]["id"])
    assert replacement.id != original.id
    assert replacement.parent_job == original
    assert replacement.version_group_id == original.version_group_id
    assert replacement.revision == 2
    assert replacement.asset_key == original.asset_key
    assert replacement.input_sha256 == original.input_sha256
    assert replacement.model_snapshot == original.model_snapshot
    assert replacement.parameters == original.parameters
    assert replacement.status == DetectionJob.Status.QUEUED

    versions = client.get(f"/api/v1/results/{replacement.id}/versions/")

    assert versions.status_code == 200
    assert [item["revision"] for item in versions.data["data"]["items"]] == [1, 2]
    assert versions.data["data"]["items"][0]["sentence"] == "你好"
    assert versions.data["data"]["items"][1]["status"] == "queued"

import hashlib
from io import BytesIO

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from PIL import Image

from detections.models import DetectionJob
from modelYolo.models import YoloModel
from storage.backends import ObjectStorage
from user.models import SysUser


def jpeg_bytes():
    buffer = BytesIO()
    Image.new("RGB", (8, 8), color=(42, 38, 97)).save(buffer, format="JPEG")
    return buffer.getvalue()


@pytest.mark.django_db
def test_backfill_hashes_updates_all_revisions_that_share_existing_media(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path / "media"
    owner = SysUser.objects.create(username="hash_backfill_owner", password="unused", status=0)
    model = YoloModel.objects.create(
        name="Hash Backfill",
        version="2.1-test",
        size="1 MB",
        status="正常",
        file_path="signflow-test.pt",
        creator=owner,
    )
    content = jpeg_bytes()
    stored = ObjectStorage().save_upload(
        SimpleUploadedFile("gesture.jpg", content, content_type="image/jpeg"),
        owner_id=owner.id,
        mode="image",
    )
    first = DetectionJob.objects.create(
        owner=owner,
        mode="image",
        asset_key=stored.key,
        model=model,
        model_snapshot={"id": model.id, "version": model.version},
        input_sha256="",
    )
    second = DetectionJob.objects.create(
        owner=owner,
        mode="image",
        asset_key=stored.key,
        model=model,
        model_snapshot={"id": model.id, "version": model.version},
        input_sha256="",
    )

    call_command("backfill_detection_hashes", limit=10)

    expected = hashlib.sha256(content).hexdigest()
    first.refresh_from_db()
    second.refresh_from_db()
    assert first.input_sha256 == expected
    assert second.input_sha256 == expected

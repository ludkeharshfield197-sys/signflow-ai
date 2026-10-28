from io import BytesIO

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image


def jpeg_bytes():
    buffer = BytesIO()
    Image.new("RGB", (4, 4), color=(42, 38, 97)).save(buffer, format="JPEG")
    return buffer.getvalue()


@pytest.mark.django_db
def test_uploaded_asset_uses_an_owner_scoped_generated_object_key(settings, tmp_path):
    from storage.backends import ObjectStorage

    settings.MEDIA_ROOT = tmp_path
    upload = SimpleUploadedFile(
        "../../private-name.jpg",
        jpeg_bytes(),
        content_type="image/jpeg",
    )

    stored = ObjectStorage().save_upload(upload, owner_id=42, mode="image")

    assert stored.key.startswith("users/42/detections/")
    assert stored.key.endswith(".jpg")
    assert ".." not in stored.key
    assert "private-name" not in stored.key
    assert ObjectStorage().exists(stored.key)


@pytest.mark.django_db
def test_upload_rejects_content_that_does_not_match_the_declared_media_type(settings, tmp_path):
    from storage.backends import ObjectStorage, UploadValidationError

    settings.MEDIA_ROOT = tmp_path
    upload = SimpleUploadedFile(
        "disguised.jpg",
        b"MZ-not-an-image-executable-payload",
        content_type="image/jpeg",
    )

    with pytest.raises(UploadValidationError, match="文件内容"):
        ObjectStorage().save_upload(upload, owner_id=42, mode="image")

    assert list(tmp_path.rglob("*")) == []


@pytest.mark.django_db
def test_object_can_be_materialized_without_exposing_a_business_absolute_path(settings, tmp_path):
    from storage.backends import ObjectStorage

    settings.MEDIA_ROOT = tmp_path
    storage = ObjectStorage()
    stored = storage.save_upload(
        SimpleUploadedFile("input.jpg", jpeg_bytes(), content_type="image/jpeg"),
        owner_id=7,
        mode="image",
    )

    with storage.materialize(stored.key) as local_path:
        assert local_path.is_file()
        assert local_path.read_bytes() == jpeg_bytes()

    assert stored.key.startswith("users/7/")

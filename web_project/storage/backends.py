import hashlib
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import date
from pathlib import Path, PurePosixPath
from tempfile import NamedTemporaryFile

from django.conf import settings
from django.core.files.storage import default_storage
from PIL import Image, UnidentifiedImageError

CONTENT_TYPE_EXTENSIONS = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "video/mp4": ".mp4",
    "video/webm": ".webm",
    "video/quicktime": ".mov",
}


@dataclass(frozen=True)
class StoredObject:
    key: str
    size: int
    content_type: str
    sha256: str


class UploadValidationError(ValueError):
    def __init__(self, message, *, code="INVALID_UPLOAD"):
        super().__init__(message)
        self.code = code


def validate_object_key(key):
    if not isinstance(key, str) or not key or "\\" in key:
        raise ValueError("Invalid object key.")
    path = PurePosixPath(key)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError("Invalid object key.")
    return path.as_posix()


def validate_upload(upload, mode):
    content_type = (getattr(upload, "content_type", "") or "").lower()
    if mode == "image":
        allowed = {"image/jpeg", "image/png", "image/webp"}
        max_bytes = settings.DETECTION_IMAGE_MAX_BYTES
    elif mode == "video":
        allowed = {"video/mp4", "video/webm", "video/quicktime"}
        max_bytes = settings.DETECTION_VIDEO_MAX_BYTES
    else:
        raise UploadValidationError("实时模式不接受文件上传。", code="MODE_MISMATCH")

    if content_type not in allowed:
        raise UploadValidationError("不支持该文件类型。", code="UNSUPPORTED_MEDIA_TYPE")
    if upload.size <= 0 or upload.size > max_bytes:
        raise UploadValidationError("文件大小超出允许范围。", code="FILE_SIZE_INVALID")

    upload.seek(0)
    try:
        if mode == "image":
            with Image.open(upload) as image:
                image.verify()
        else:
            signature = upload.read(32)
            is_mp4 = content_type in {"video/mp4", "video/quicktime"} and signature[4:8] == b"ftyp"
            is_webm = content_type == "video/webm" and signature.startswith(b"\x1aE\xdf\xa3")
            if not (is_mp4 or is_webm):
                raise UploadValidationError(
                    "文件内容与声明的媒体类型不一致。",
                    code="CONTENT_MISMATCH",
                )
    except (UnidentifiedImageError, OSError, SyntaxError) as exc:
        raise UploadValidationError(
            "文件内容与声明的媒体类型不一致。",
            code="CONTENT_MISMATCH",
        ) from exc
    finally:
        upload.seek(0)


class ObjectStorage:
    def save_upload(self, upload, *, owner_id, mode):
        if mode not in {"image", "video", "live"}:
            raise ValueError("Unsupported detection mode.")
        validate_upload(upload, mode)
        content_type = (getattr(upload, "content_type", "") or "").lower()
        extension = CONTENT_TYPE_EXTENSIONS.get(content_type)
        if extension is None:
            raise ValueError("Unsupported upload content type.")
        today = date.today()
        key = f"users/{int(owner_id)}/detections/{today:%Y/%m}/{uuid.uuid4().hex}{extension}"
        digest = hashlib.sha256()
        upload.seek(0)
        for chunk in upload.chunks():
            digest.update(chunk)
        upload.seek(0)
        stored_key = default_storage.save(validate_object_key(key), upload)
        return StoredObject(
            key=validate_object_key(stored_key),
            size=default_storage.size(stored_key),
            content_type=content_type,
            sha256=digest.hexdigest(),
        )

    def exists(self, key):
        return default_storage.exists(validate_object_key(key))

    def open(self, key):
        return default_storage.open(validate_object_key(key), "rb")

    @contextmanager
    def materialize(self, key):
        safe_key = validate_object_key(key)
        try:
            local_path = Path(default_storage.path(safe_key)).resolve()
        except (AttributeError, NotImplementedError):
            suffix = PurePosixPath(safe_key).suffix
            temporary = NamedTemporaryFile(prefix="signflow-", suffix=suffix, delete=False)
            temporary_path = Path(temporary.name)
            try:
                with temporary, default_storage.open(safe_key, "rb") as source:
                    for chunk in iter(lambda: source.read(1024 * 1024), b""):
                        temporary.write(chunk)
                yield temporary_path
            finally:
                temporary_path.unlink(missing_ok=True)
        else:
            yield local_path

    def delete(self, key):
        default_storage.delete(validate_object_key(key))

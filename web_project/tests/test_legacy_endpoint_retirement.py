from pathlib import Path

import pytest
from django.test import RequestFactory

WEB_PROJECT_ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(
    "relative_path",
    [
        "ImageModel/views.py",
        "videoModel/views.py",
        "CameraModel/views.py",
    ],
)
def test_retired_media_views_do_not_load_models_or_contain_embedded_secrets(relative_path):
    source = (WEB_PROJECT_ROOT / relative_path).read_text(encoding="utf-8")

    assert "from ultralytics import" not in source
    assert "torch.hub.load" not in source
    assert "threading.Thread" not in source
    assert "sk-" not in source


def test_legacy_media_endpoint_returns_a_migration_response():
    from ImageModel.views import ImageDetectView

    response = ImageDetectView.as_view()(RequestFactory().post("/legacy/image/detect/"))

    assert response.status_code == 410
    assert response.headers["Deprecation"] == "true"
    assert b"/api/v1/detections/" in response.content

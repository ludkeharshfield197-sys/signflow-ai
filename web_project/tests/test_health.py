from unittest.mock import patch

import pytest
from rest_framework.test import APIClient


def test_liveness_only_reports_the_web_process():
    response = APIClient().get("/health/live")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "signflow-api",
    }


@pytest.mark.django_db
def test_readiness_reports_each_required_dependency():
    healthy = {"ok": True, "latencyMs": 1}
    with (
        patch("health.views.check_database", return_value=healthy),
        patch("health.views.check_cache", return_value=healthy),
        patch("health.views.check_object_storage", return_value=healthy),
        patch("health.views.check_model_service", return_value=healthy),
    ):
        response = APIClient().get("/health/ready")

    assert response.status_code == 200
    assert response.json()["status"] == "ready"
    assert set(response.json()["checks"]) == {"database", "redis", "objectStorage", "modelService"}


@pytest.mark.django_db
def test_readiness_returns_503_without_leaking_dependency_exception_details():
    with (
        patch("health.views.check_database", side_effect=RuntimeError("password=do-not-leak")),
        patch("health.views.check_cache", return_value={"ok": True}),
        patch("health.views.check_object_storage", return_value={"ok": True}),
        patch("health.views.check_model_service", return_value={"ok": True}),
    ):
        response = APIClient().get("/health/ready")

    assert response.status_code == 503
    body = response.json()
    assert body["status"] == "unavailable"
    assert body["checks"]["database"] == {"ok": False, "code": "DEPENDENCY_UNAVAILABLE"}
    assert "password" not in response.content.decode("utf-8")

import importlib
import os
import sys

import pytest
from django.core.exceptions import ImproperlyConfigured


def _reload_prod():
    sys.modules.pop("web_project.settings.prod", None)
    return importlib.import_module("web_project.settings.prod")


def test_production_settings_refuse_to_start_without_a_secret(monkeypatch):
    monkeypatch.delenv("DJANGO_SECRET_KEY", raising=False)

    with pytest.raises(ImproperlyConfigured, match="DJANGO_SECRET_KEY"):
        _reload_prod()


def test_production_settings_are_closed_and_environment_driven(monkeypatch, tmp_path):
    values = {
        "DJANGO_SECRET_KEY": "s" * 64,
        "DJANGO_ALLOWED_HOSTS": "signflow.example.test",
        "CORS_ALLOWED_ORIGINS": "https://signflow.example.test",
        "CSRF_TRUSTED_ORIGINS": "https://signflow.example.test",
        "DB_NAME": "signflow",
        "DB_USER": "signflow",
        "DB_PASSWORD": "database-test-value",
        "DB_HOST": "database",
        "DB_PORT": "3306",
        "MODEL_STORAGE_ROOT": str(tmp_path / "models"),
        "MEDIA_STORAGE_BACKEND": "s3",
        "MEDIA_STORAGE_BUCKET": "signflow-media",
        "MEDIA_STORAGE_ENDPOINT": "https://storage.example.test",
        "MEDIA_STORAGE_ACCESS_KEY": "test-access-key",
        "MEDIA_STORAGE_SECRET_KEY": "test-secret-key",
    }
    for name, value in values.items():
        monkeypatch.setenv(name, value)

    prod = _reload_prod()

    assert prod.DEBUG is False
    assert "*" not in prod.ALLOWED_HOSTS
    assert prod.CORS_ALLOW_ALL_ORIGINS is False
    assert not prod.SECRET_KEY.startswith("django-insecure")
    assert prod.AUTH_COOKIE_SECURE is True
    assert prod.SESSION_COOKIE_SECURE is True
    assert prod.CSRF_COOKIE_SECURE is True
    assert prod.SECURE_SSL_REDIRECT is True
    assert prod.SECURE_HSTS_SECONDS == 3600
    assert prod.SECURE_HSTS_INCLUDE_SUBDOMAINS is False
    assert prod.SECURE_HSTS_PRELOAD is False
    assert prod.ENABLE_LEGACY_ENDPOINTS is False


def test_development_jwt_uses_the_effective_django_secret():
    from web_project.settings import dev

    assert dev.SIMPLE_JWT["SIGNING_KEY"] == dev.SECRET_KEY
    assert dev.SIMPLE_JWT["SIGNING_KEY"]


def test_ultralytics_dependency_auto_install_is_disabled_by_default(monkeypatch):
    monkeypatch.delenv("YOLO_AUTOINSTALL", raising=False)
    importlib.reload(importlib.import_module("web_project.settings.base"))

    assert os.environ["YOLO_AUTOINSTALL"] == "false"

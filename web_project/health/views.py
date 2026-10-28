import os
import time
from pathlib import Path

from django.conf import settings
from django.core.cache import cache
from django.core.files.storage import default_storage
from django.db import connection
from django.http import JsonResponse


def _result(check):
    started = time.perf_counter()
    check()
    return {
        "ok": True,
        "latencyMs": max(round((time.perf_counter() - started) * 1000), 0),
    }


def check_database():
    def probe():
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()

    return _result(probe)


def check_cache():
    def probe():
        key = "signflow:health:ready"
        cache.set(key, "ok", timeout=10)
        if cache.get(key) != "ok":
            raise RuntimeError("Cache readiness probe failed.")
        cache.delete(key)

    return _result(probe)


def check_object_storage():
    def probe():
        storage = default_storage
        bucket_name = getattr(storage, "bucket_name", "")
        if bucket_name:
            storage.connection.meta.client.head_bucket(Bucket=bucket_name)
            return
        location = Path(getattr(storage, "location", settings.MEDIA_ROOT)).resolve()
        if not location.is_dir() or not os.access(location, os.R_OK | os.W_OK):
            raise RuntimeError("Local object storage is unavailable.")

    return _result(probe)


def check_model_service():
    def probe():
        root = Path(settings.MODELS_ROOT).resolve()
        if not root.is_dir():
            raise RuntimeError("Model storage is unavailable.")
        if not any(path.is_file() for path in root.glob("*.pt")):
            raise RuntimeError("No deployable model weights are available.")

    return _result(probe)


def readiness_payload():
    checks = {}
    probes = {
        "database": check_database,
        "redis": check_cache,
        "objectStorage": check_object_storage,
        "modelService": check_model_service,
    }
    for name, probe in probes.items():
        try:
            checks[name] = probe()
        except Exception:
            checks[name] = {
                "ok": False,
                "code": "DEPENDENCY_UNAVAILABLE",
            }
    ready = all(check.get("ok") is True for check in checks.values())
    return {
        "status": "ready" if ready else "unavailable",
        "service": "signflow-api",
        "checks": checks,
    }, ready


def live(request):
    return JsonResponse({"status": "ok", "service": "signflow-api"})


def ready(request):
    payload, is_ready = readiness_payload()
    return JsonResponse(payload, status=200 if is_ready else 503)

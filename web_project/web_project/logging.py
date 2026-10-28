import json
import logging
import time
from datetime import datetime, timezone


class JsonFormatter(logging.Formatter):
    def format(self, record):
        payload = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "requestId": getattr(record, "request_id", None),
            "route": getattr(record, "route", None),
            "status": getattr(record, "status", None),
            "durationMs": getattr(record, "duration_ms", None),
            "userId": getattr(record, "user_id", None),
            "jobId": getattr(record, "job_id", None),
            "errorType": getattr(record, "error_type", None),
            "sessionId": getattr(record, "session_id", None),
            "frameId": getattr(record, "frame_id", None),
        }
        if record.exc_info:
            exception_type = record.exc_info[0] if isinstance(record.exc_info, tuple) else None
            payload["exception"] = (
                exception_type.__name__
                if exception_type is not None
                else getattr(record, "error_type", "Exception")
            )
        return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


class StructuredRequestLoggingMiddleware:
    logger = logging.getLogger("signflow.request")

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        started = time.perf_counter()
        try:
            response = self.get_response(request)
        except Exception:
            self._log(request, status=500, started=started, level=logging.ERROR)
            raise
        self._log(request, status=response.status_code, started=started)
        return response

    def _log(self, request, *, status, started, level=logging.INFO):
        self.logger.log(
            level,
            "HTTP request completed",
            extra={
                "request_id": getattr(request, "request_id", None),
                "route": request.path,
                "status": status,
                "duration_ms": max(round((time.perf_counter() - started) * 1000), 0),
                "user_id": getattr(request, "signflow_user_id", None),
            },
        )

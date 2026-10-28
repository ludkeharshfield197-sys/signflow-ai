import json
import logging
import sys

from django.http import JsonResponse
from django.test import RequestFactory


def test_request_log_contains_operational_fields_without_sensitive_headers(caplog):
    from web_project.logging import StructuredRequestLoggingMiddleware

    request = RequestFactory().post(
        "/api/v1/auth/login/",
        data={"username": "competitor", "password": "do-not-log"},
        content_type="application/json",
        HTTP_AUTHORIZATION="Bearer do-not-log-this-token",
    )
    request.request_id = "req-product-01"
    request.signflow_user_id = 34
    middleware = StructuredRequestLoggingMiddleware(
        lambda current_request: JsonResponse({"success": True}, status=201),
    )

    with caplog.at_level(logging.INFO, logger="signflow.request"):
        response = middleware(request)

    record = caplog.records[-1]
    assert response.status_code == 201
    assert record.request_id == "req-product-01"
    assert record.route == "/api/v1/auth/login/"
    assert record.status == 201
    assert record.user_id == 34
    assert isinstance(record.duration_ms, int)
    assert "do-not-log" not in record.getMessage()


def test_json_formatter_keeps_safe_job_context_and_exception_type():
    from web_project.logging import JsonFormatter

    try:
        raise ValueError("sensitive internal detail")
    except ValueError:
        record = logging.getLogger("detections.test").makeRecord(
            "detections.test",
            logging.ERROR,
            __file__,
            1,
            "Detection job failed",
            (),
            exc_info=sys.exc_info(),
            extra={
                "job_id": "det_test_01",
                "error_type": "ValueError",
            },
        )

    payload = json.loads(JsonFormatter().format(record))

    assert payload["jobId"] == "det_test_01"
    assert payload["errorType"] == "ValueError"
    assert payload["exception"] == "ValueError"
    assert "sensitive internal detail" not in payload.values()

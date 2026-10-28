from rest_framework.views import exception_handler as drf_exception_handler

from api.response import error_response


def _first_message(value):
    if isinstance(value, dict):
        for item in value.values():
            return _first_message(item)
    if isinstance(value, (list, tuple)) and value:
        return _first_message(value[0])
    return str(value)


def api_exception_handler(exc, context):
    response = drf_exception_handler(exc, context)
    if response is None:
        return None

    codes = exc.get_codes() if hasattr(exc, "get_codes") else "api_error"
    code = _first_message(codes)
    message = _first_message(response.data)
    request = context["request"]
    return error_response(
        request,
        code,
        message,
        status=response.status_code,
        details=response.data if isinstance(response.data, dict) else None,
    )

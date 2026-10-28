import uuid

from rest_framework.response import Response


def get_request_id(request):
    request_id = getattr(request, "request_id", "")
    if request_id:
        return request_id
    return uuid.uuid4().hex


def success_response(request, data=None, *, status=200):
    return Response(
        {
            "success": True,
            "data": data if data is not None else {},
            "error": None,
            "requestId": get_request_id(request),
        },
        status=status,
    )


def error_response(request, code, message, *, status=400, details=None):
    error = {"code": code, "message": message}
    if details:
        error["details"] = details
    return Response(
        {
            "success": False,
            "data": None,
            "error": error,
            "requestId": get_request_id(request),
        },
        status=status,
    )

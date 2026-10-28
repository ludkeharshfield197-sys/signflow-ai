import re
import uuid

REQUEST_ID_PATTERN = re.compile(r"^[A-Za-z0-9._:-]{8,128}$")


class RequestIdMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        candidate = request.headers.get("X-Request-ID", "")
        request.request_id = (
            candidate if REQUEST_ID_PATTERN.fullmatch(candidate) else uuid.uuid4().hex
        )
        response = self.get_response(request)
        response["X-Request-ID"] = request.request_id
        return response


class SecurityHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response.setdefault(
            "Content-Security-Policy",
            "default-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'",
        )
        response.setdefault("Permissions-Policy", "camera=(self), microphone=(), geolocation=()")
        response.setdefault("Cross-Origin-Resource-Policy", "same-site")
        return response

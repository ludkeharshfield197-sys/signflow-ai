from django.http import JsonResponse
from django.views import View


def retired_media_endpoint(request, *args, **kwargs):
    response = JsonResponse(
        {
            "success": False,
            "data": None,
            "error": {
                "code": "LEGACY_ENDPOINT_RETIRED",
                "message": "该旧版媒体接口已停用，请迁移到 /api/v1/detections/。",
            },
        },
        status=410,
    )
    response["Deprecation"] = "true"
    response["Sunset"] = "Wed, 29 Jul 2026 00:00:00 GMT"
    response["Link"] = '</api/v1/detections/>; rel="successor-version"'
    response["Cache-Control"] = "no-store"
    return response


class RetiredMediaEndpointView(View):
    def dispatch(self, request, *args, **kwargs):
        return retired_media_endpoint(request, *args, **kwargs)

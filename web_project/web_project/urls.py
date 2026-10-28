from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

urlpatterns = [
    path("api/v1/", include("api.urls")),
    path("health/", include("health.urls")),
]

if settings.ENABLE_LEGACY_ENDPOINTS:
    urlpatterns += [
        path("user/", include("user.urls")),
        path("role/", include("role.urls")),
        path("menu/", include("menu.urls")),
        path("modelYolo/", include("modelYolo.urls")),
        path("image/", include("ImageModel.urls")),
        path("video/", include("videoModel.urls")),
        path("camera/", include("CameraModel.urls")),
        path("agent/", include("Agent.urls")),
    ]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

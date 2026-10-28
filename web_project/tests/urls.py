from django.urls import include, path

try:
    import api.urls  # noqa: F401
except ModuleNotFoundError:
    urlpatterns = []
else:
    urlpatterns = [
        path("api/v1/", include("api.urls")),
        path("health/", include("health.urls")),
    ]

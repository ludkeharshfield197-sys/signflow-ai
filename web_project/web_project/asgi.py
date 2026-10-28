import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "web_project.settings.dev")

from channels.routing import ProtocolTypeRouter, URLRouter
from django.conf import settings
from django.core.asgi import get_asgi_application

django_asgi_application = get_asgi_application()
websocket_urlpatterns = []
if settings.ENABLE_CAMERA_WEBSOCKET:
    from api.channels import CameraTicketAuthMiddleware
    from CameraModel.routing import websocket_urlpatterns as camera_websocket_urlpatterns

    websocket_urlpatterns.extend(camera_websocket_urlpatterns)

application = ProtocolTypeRouter(
    {
        "http": django_asgi_application,
        "websocket": CameraTicketAuthMiddleware(URLRouter(websocket_urlpatterns))
        if settings.ENABLE_CAMERA_WEBSOCKET
        else URLRouter(websocket_urlpatterns),
    }
)

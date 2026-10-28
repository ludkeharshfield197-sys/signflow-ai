from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/camera/<str:session_id>/', consumers.CameraConsumer.as_asgi()),
]



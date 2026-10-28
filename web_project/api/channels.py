import uuid
from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.conf import settings
from django.core import signing
from django.core.cache import cache
from django.db.models import Q

from user.models import SysUser

TICKET_SALT = "signflow.camera.websocket"


def issue_camera_ticket(user):
    jti = uuid.uuid4().hex
    ttl = getattr(settings, "CAMERA_TICKET_SECONDS", 60)
    cache.set(f"camera:ticket:{jti}", user.id, timeout=ttl)
    return signing.dumps({"jti": jti}, salt=TICKET_SALT, compress=True)


def consume_camera_ticket(ticket):
    ttl = getattr(settings, "CAMERA_TICKET_SECONDS", 60)
    try:
        payload = signing.loads(ticket, salt=TICKET_SALT, max_age=ttl)
        jti = payload["jti"]
    except (KeyError, signing.BadSignature, signing.SignatureExpired):
        return None
    if not cache.add(f"camera:ticket-lock:{jti}", True, timeout=5):
        return None
    key = f"camera:ticket:{jti}"
    user_id = cache.get(key)
    cache.delete(key)
    if not user_id:
        return None
    return SysUser.objects.filter(pk=user_id).filter(Q(status=0) | Q(status__isnull=True)).first()


class CameraTicketAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        query = parse_qs(scope.get("query_string", b"").decode("utf-8", errors="ignore"))
        ticket = query.get("ticket", [""])[0]
        scope = dict(scope)
        scope["sys_user"] = await database_sync_to_async(consume_camera_ticket)(ticket)
        return await super().__call__(scope, receive, send)

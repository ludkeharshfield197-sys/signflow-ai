from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from api.authentication import SysUserJWTAuthentication
from api.response import error_response
from api.views import LoginAPIView, RegisterAPIView


class LoginView(LoginAPIView):
    """Compatibility alias for installations migrating from /user/login."""


class RegisterView(RegisterAPIView):
    """Compatibility alias for installations migrating from /user/register."""


class LegacyRetiredView(APIView):
    authentication_classes = [SysUserJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def _retired(self, request):
        return error_response(
            request,
            "LEGACY_ENDPOINT_RETIRED",
            "该管理接口已迁移到 /api/v1，旧接口不再提供写入能力。",
            status=410,
        )

    get = _retired
    post = _retired
    put = _retired
    patch = _retired
    delete = _retired


SaveView = LegacyRetiredView
PwdView = LegacyRetiredView
ImageView = LegacyRetiredView
AvatarView = LegacyRetiredView
SearchView = LegacyRetiredView
ActionView = LegacyRetiredView
CheckView = LegacyRetiredView
PasswordView = LegacyRetiredView
StatusView = LegacyRetiredView
GrantRole = LegacyRetiredView


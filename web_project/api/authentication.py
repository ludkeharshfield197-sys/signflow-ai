from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.settings import api_settings

from user.models import SysUser


class SysUserJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        result = super().authenticate(request)
        if result is not None:
            user, _ = result
            raw_request = getattr(request, "_request", request)
            raw_request.signflow_user_id = user.id
        return result

    def get_user(self, validated_token):
        try:
            user_id = validated_token[api_settings.USER_ID_CLAIM]
        except KeyError as exc:
            raise AuthenticationFailed("令牌缺少用户标识。", code="token_not_valid") from exc
        try:
            user = SysUser.objects.get(pk=user_id)
        except SysUser.DoesNotExist as exc:
            raise AuthenticationFailed("用户不存在。", code="user_not_found") from exc
        if not user.is_active:
            raise AuthenticationFailed("账号已停用。", code="user_inactive")
        return user

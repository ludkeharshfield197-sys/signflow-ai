from django.conf import settings
from django.db import transaction
from django.utils import timezone
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from api.authentication import SysUserJWTAuthentication
from api.channels import issue_camera_ticket
from api.response import error_response, success_response
from api.serializers import LoginSerializer, RegisterSerializer, SafeUserSerializer
from role.models import SysRole, SysUserRole
from user.models import SysUser


class LoginAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                request,
                "VALIDATION_ERROR",
                "请提供有效的账号和密码。",
                status=400,
                details=serializer.errors,
            )

        username = serializer.validated_data["username"]
        password = serializer.validated_data["password"]
        try:
            user = SysUser.objects.get(username=username)
        except SysUser.DoesNotExist:
            return error_response(request, "INVALID_CREDENTIALS", "账号或密码错误。", status=401)

        if not user.is_active or not user.check_password(password):
            return error_response(request, "INVALID_CREDENTIALS", "账号或密码错误。", status=401)

        user.login_date = timezone.localdate()
        user.save(update_fields=["login_date"])
        refresh = RefreshToken.for_user(user)
        roles = list(
            SysUserRole.objects.filter(user=user)
            .order_by("role_id")
            .values_list("role__name", flat=True)
        )
        response = success_response(
            request,
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": SafeUserSerializer(user).data,
                "roles": roles,
            },
        )
        response.set_cookie(
            settings.AUTH_REFRESH_COOKIE,
            str(refresh),
            max_age=int(refresh.lifetime.total_seconds()),
            secure=settings.AUTH_COOKIE_SECURE,
            httponly=True,
            samesite=settings.AUTH_COOKIE_SAMESITE,
            path="/api/v1/auth/",
        )
        return response


class RegisterAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"

    @transaction.atomic
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                request,
                "VALIDATION_ERROR",
                "注册信息不符合要求。",
                status=400,
                details=serializer.errors,
            )

        data = serializer.validated_data
        user = SysUser(
            username=data["username"],
            email=data.get("email") or None,
            avatar="default.jpg",
            status=0,
            create_time=timezone.localdate(),
            update_time=timezone.localdate(),
        )
        user.set_password(data["password"])
        user.save()
        role = SysRole.objects.filter(code="user").order_by("id").first()
        if role is None:
            role = SysRole.objects.create(name="普通用户", code="user")
        SysUserRole.objects.create(user=user, role=role)
        return success_response(request, {"user": SafeUserSerializer(user).data}, status=201)


class RefreshAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"

    def post(self, request):
        # Browser clients renew through the HttpOnly cookie. Native and
        # mini-program runtimes do not reliably persist cookies, so they may
        # submit the same bearer refresh token in the JSON body.
        encoded_refresh = request.COOKIES.get(settings.AUTH_REFRESH_COOKIE)
        if not encoded_refresh:
            body_refresh = request.data.get("refresh") if hasattr(request.data, "get") else None
            if isinstance(body_refresh, str):
                encoded_refresh = body_refresh.strip()
        if not encoded_refresh:
            return error_response(
                request, "REFRESH_REQUIRED", "登录状态已失效，请重新登录。", status=401
            )
        try:
            refresh = RefreshToken(encoded_refresh)
            user = SysUser.objects.get(pk=refresh["user_id"])
        except (KeyError, SysUser.DoesNotExist, TokenError):
            return error_response(
                request, "INVALID_REFRESH", "登录状态已失效，请重新登录。", status=401
            )
        if not user.is_active:
            return error_response(request, "ACCOUNT_DISABLED", "账号已停用。", status=403)

        roles = list(
            SysUserRole.objects.filter(user=user)
            .order_by("role_id")
            .values_list("role__name", flat=True)
        )
        return success_response(
            request,
            {
                "access": str(refresh.access_token),
                "user": SafeUserSerializer(user).data,
                "roles": roles,
            },
        )


class MeAPIView(APIView):
    authentication_classes = [SysUserJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        roles = list(
            SysUserRole.objects.filter(user=request.user)
            .order_by("role_id")
            .values_list("role__name", flat=True)
        )
        return success_response(
            request,
            {
                "user": SafeUserSerializer(request.user).data,
                "roles": roles,
            },
        )


class LogoutAPIView(APIView):
    authentication_classes = [SysUserJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        response = success_response(request, {"loggedOut": True})
        response.delete_cookie(
            settings.AUTH_REFRESH_COOKIE,
            path="/api/v1/auth/",
            samesite=settings.AUTH_COOKIE_SAMESITE,
        )
        return response


class CameraTicketAPIView(APIView):
    authentication_classes = [SysUserJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return success_response(
            request,
            {
                "ticket": issue_camera_ticket(request.user),
                "expiresIn": getattr(settings, "CAMERA_TICKET_SECONDS", 60),
            },
            status=201,
        )

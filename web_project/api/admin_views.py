from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.views import APIView

from api.authentication import SysUserJWTAuthentication
from api.response import error_response, success_response
from detections.models import DetectionJob
from health.views import readiness_payload
from modelYolo.models import YoloModel
from role.models import SysRole, SysUserRole
from user.models import SysUser

ADMIN_ROLE_CODES = {"admin", "superadmin"}


class HasAdminRole(BasePermission):
    message = "只有管理员可以访问该区域。"

    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        return bool(
            user
            and user.is_authenticated
            and SysUserRole.objects.filter(
                user=user,
                role__code__in=ADMIN_ROLE_CODES,
            ).exists()
        )


class AdminAPIView(APIView):
    authentication_classes = [SysUserJWTAuthentication]
    permission_classes = [IsAuthenticated, HasAdminRole]


def _masked_email(value):
    if not value or "@" not in value:
        return "未设置"
    local, domain = value.split("@", 1)
    return f"{local[:1]}***@{domain}"


def _date_value(value):
    return value.isoformat() if value else None


class AdminUserListAPIView(AdminAPIView):
    def get(self, request):
        queryset = SysUser.objects.all().order_by("-create_time", "-id")
        query = request.query_params.get("query", "").strip()
        if query:
            queryset = queryset.filter(Q(username__icontains=query) | Q(email__icontains=query))
        try:
            page_number = max(int(request.query_params.get("page", 1)), 1)
            page_size = min(max(int(request.query_params.get("pageSize", 20)), 1), 100)
        except ValueError:
            return error_response(request, "VALIDATION_ERROR", "分页参数无效。", status=400)

        paginator = Paginator(queryset, page_size)
        page = paginator.get_page(page_number)
        role_map = {}
        links = (
            SysUserRole.objects.filter(user_id__in=[user.id for user in page.object_list])
            .select_related("role")
            .order_by("role_id")
        )
        for link in links:
            role_map.setdefault(link.user_id, []).append(link.role.name or link.role.code)

        items = [
            {
                "id": user.id,
                "username": user.username,
                "email": _masked_email(user.email),
                "status": "active" if user.is_active else "disabled",
                "statusLabel": "正常" if user.is_active else "已停用",
                "roles": role_map.get(user.id, []),
                "lastLoginAt": _date_value(user.login_date),
                "createdAt": _date_value(user.create_time),
            }
            for user in page.object_list
        ]
        return success_response(
            request,
            {
                "items": items,
                "page": page.number,
                "pageSize": page_size,
                "total": paginator.count,
                "source": "SignFlow AI 用户数据库",
            },
        )


class AdminRoleListAPIView(AdminAPIView):
    def get(self, request):
        items = [
            {
                "id": role.id,
                "name": role.name or "未命名角色",
                "code": role.code or "",
                "description": role.remark or "暂无角色说明",
                "userCount": SysUserRole.objects.filter(role=role).count(),
                "createdAt": _date_value(role.create_time),
                "updatedAt": _date_value(role.update_time),
            }
            for role in SysRole.objects.all().order_by("id")
        ]
        return success_response(
            request,
            {
                "items": items,
                "total": len(items),
                "source": "SignFlow AI 权限数据库",
            },
        )


class AdminSystemAPIView(AdminAPIView):
    def get(self, request):
        readiness, _ = readiness_payload()
        return success_response(
            request,
            {
                "status": readiness["status"],
                "service": readiness["service"],
                "checks": readiness["checks"],
                "counts": {
                    "users": SysUser.objects.count(),
                    "roles": SysRole.objects.count(),
                    "models": YoloModel.objects.count(),
                    "tasks": DetectionJob.objects.count(),
                },
                "environment": "development" if settings.DEBUG else "production",
                "retentionDays": getattr(settings, "DETECTION_RETENTION_DAYS", 30),
                "updatedAt": timezone.now().isoformat(),
                "source": "SignFlow AI 健康检查与业务数据库",
            },
        )

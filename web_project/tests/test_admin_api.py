from unittest.mock import patch

import pytest
from rest_framework.test import APIClient

from modelYolo.models import YoloModel
from role.models import SysRole, SysUserRole
from user.models import SysUser


def create_user_with_role(username, role_code):
    user = SysUser.objects.create(
        username=username,
        password="unused",
        email=f"{username}@example.test",
        phonenumber="13800000000",
        status=0,
    )
    role = SysRole.objects.create(name=role_code.title(), code=role_code)
    SysUserRole.objects.create(user=user, role=role)
    return user


@pytest.mark.django_db
def test_admin_console_returns_safe_real_users_and_roles():
    admin = create_user_with_role("console_admin", "superadmin")
    member = create_user_with_role("console_member", "user")
    client = APIClient()
    client.force_authenticate(user=admin)

    users_response = client.get("/api/v1/admin/users/")
    roles_response = client.get("/api/v1/admin/roles/")

    assert users_response.status_code == 200
    users = users_response.data["data"]["items"]
    member_payload = next(item for item in users if item["id"] == member.id)
    assert member_payload["username"] == "console_member"
    assert member_payload["email"] == "c***@example.test"
    assert member_payload["roles"] == ["User"]
    assert "password" not in member_payload
    assert "phonenumber" not in member_payload

    assert roles_response.status_code == 200
    roles = roles_response.data["data"]["items"]
    user_role = next(item for item in roles if item["code"] == "user")
    assert user_role["userCount"] == 1


@pytest.mark.django_db
def test_non_admin_cannot_read_admin_console():
    member = create_user_with_role("regular_member", "user")
    client = APIClient()
    client.force_authenticate(user=member)

    for path in (
        "/api/v1/admin/users/",
        "/api/v1/admin/roles/",
        "/api/v1/admin/system/",
    ):
        response = client.get(path)
        assert response.status_code == 403


@pytest.mark.django_db
def test_admin_system_summary_uses_database_counts_and_readiness():
    admin = create_user_with_role("system_admin", "admin")
    YoloModel.objects.create(
        name="System Summary Model",
        version="1.0",
        size="1 MB",
        status="正常",
        file_path="summary.pt",
        creator=admin,
    )
    client = APIClient()
    client.force_authenticate(user=admin)

    with patch(
        "api.admin_views.readiness_payload",
        return_value=(
            {
                "status": "ready",
                "service": "signflow-api",
                "checks": {
                    "database": {"ok": True, "latencyMs": 1},
                    "redis": {"ok": True, "latencyMs": 2},
                    "objectStorage": {"ok": True, "latencyMs": 1},
                    "modelService": {"ok": True, "latencyMs": 3},
                },
            },
            True,
        ),
    ):
        response = client.get("/api/v1/admin/system/")

    assert response.status_code == 200
    payload = response.data["data"]
    assert payload["status"] == "ready"
    assert payload["counts"]["users"] == 1
    assert payload["counts"]["models"] == 1
    assert payload["checks"]["modelService"]["ok"] is True
    assert "secret" not in str(payload).lower()

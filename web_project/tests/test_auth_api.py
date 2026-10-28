import hashlib

import pytest
from django.contrib.auth.hashers import check_password, make_password
from django.core.cache import cache
from rest_framework.test import APIClient

from role.models import SysRole, SysUserRole
from user.models import SysUser


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture(autouse=True)
def clear_api_cache():
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def user(db):
    account = SysUser.objects.create(
        username="product_admin",
        password=make_password("Correct-Horse-2026"),
        email="admin@example.test",
        status=0,
    )
    role = SysRole.objects.create(name="超级管理员", code="admin")
    SysUserRole.objects.create(user=account, role=role)
    return account


def test_login_accepts_json_and_never_returns_password(api_client, user):
    response = api_client.post(
        "/api/v1/auth/login/",
        {"username": user.username, "password": "Correct-Horse-2026"},
        format="json",
    )

    assert response.status_code == 200
    assert response.data["success"] is True
    assert response.data["error"] is None
    assert response.data["requestId"]
    assert response.data["data"]["access"]
    assert response.data["data"]["refresh"]
    assert "password" not in response.data["data"]["user"]
    assert response.cookies["signflow_refresh"]["httponly"] is True


def test_login_upgrades_a_legacy_md5_password(api_client, user):
    user.password = hashlib.md5("Legacy-Password-2026".encode("utf-8")).hexdigest()
    user.save(update_fields=["password"])

    response = api_client.post(
        "/api/v1/auth/login/",
        {"username": user.username, "password": "Legacy-Password-2026"},
        format="json",
    )

    assert response.status_code == 200
    user.refresh_from_db()
    assert user.password != hashlib.md5("Legacy-Password-2026".encode("utf-8")).hexdigest()
    assert check_password("Legacy-Password-2026", user.password)


def test_register_hashes_the_password_and_returns_only_safe_fields(api_client, db):
    SysRole.objects.create(name="普通用户", code="user")

    response = api_client.post(
        "/api/v1/auth/register/",
        {
            "username": "new_competitor",
            "email": "competitor@example.test",
            "password": "Strong-Password-2026",
            "confirmPassword": "Strong-Password-2026",
        },
        format="json",
    )

    assert response.status_code == 201
    assert response.data["success"] is True
    assert "password" not in response.data["data"]["user"]
    account = SysUser.objects.get(username="new_competitor")
    assert account.password != "Strong-Password-2026"
    assert check_password("Strong-Password-2026", account.password)
    assert SysUserRole.objects.filter(user=account, role__code="user").exists()


def test_refresh_rotates_access_using_the_http_only_cookie(api_client, user):
    login_response = api_client.post(
        "/api/v1/auth/login/",
        {"username": user.username, "password": "Correct-Horse-2026"},
        format="json",
    )
    original_access = login_response.data["data"]["access"]

    response = api_client.post("/api/v1/auth/refresh/", {}, format="json")

    assert response.status_code == 200
    assert response.data["data"]["access"]
    assert response.data["data"]["access"] != original_access
    assert "refresh" not in response.data["data"]


def test_refresh_accepts_json_token_for_native_clients(api_client, user):
    login_response = api_client.post(
        "/api/v1/auth/login/",
        {"username": user.username, "password": "Correct-Horse-2026"},
        format="json",
    )
    refresh = login_response.data["data"]["refresh"]
    original_access = login_response.data["data"]["access"]
    native_client = APIClient()

    response = native_client.post(
        "/api/v1/auth/refresh/",
        {"refresh": refresh},
        format="json",
    )

    assert response.status_code == 200
    assert response.data["data"]["access"]
    assert response.data["data"]["access"] != original_access
    assert "refresh" not in response.data["data"]


def test_me_requires_a_bearer_token_and_returns_a_safe_user(api_client, user):
    anonymous_response = api_client.get("/api/v1/auth/me/")
    login_response = api_client.post(
        "/api/v1/auth/login/",
        {"username": user.username, "password": "Correct-Horse-2026"},
        format="json",
    )
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {login_response.data['data']['access']}")

    response = api_client.get("/api/v1/auth/me/")

    assert anonymous_response.status_code == 401
    assert response.status_code == 200
    assert response.data["data"]["user"]["username"] == user.username
    assert "password" not in response.data["data"]["user"]
    assert response.data["data"]["roles"] == ["超级管理员"]


def test_logout_clears_the_refresh_cookie(api_client, user):
    login_response = api_client.post(
        "/api/v1/auth/login/",
        {"username": user.username, "password": "Correct-Horse-2026"},
        format="json",
    )
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {login_response.data['data']['access']}")

    response = api_client.post("/api/v1/auth/logout/", {}, format="json")

    assert response.status_code == 200
    assert response.cookies["signflow_refresh"].value == ""
    assert response.cookies["signflow_refresh"]["max-age"] == 0


def test_authentication_errors_use_the_standard_api_contract(api_client, db):
    response = api_client.get("/api/v1/auth/me/")

    assert response.status_code == 401
    assert response.data["success"] is False
    assert response.data["data"] is None
    assert response.data["error"]["code"] == "not_authenticated"
    assert response.data["requestId"]


def test_login_rate_limits_repeated_failures(api_client, user):
    payload = {"username": user.username, "password": "Wrong-Password-2026"}

    first = api_client.post("/api/v1/auth/login/", payload, format="json")
    second = api_client.post("/api/v1/auth/login/", payload, format="json")
    third = api_client.post("/api/v1/auth/login/", payload, format="json")

    assert first.status_code == 401
    assert second.status_code == 401
    assert third.status_code == 429
    assert third.data["error"]["code"] == "throttled"


def test_login_ignores_credentials_supplied_in_the_url(api_client, user):
    response = api_client.post(
        f"/api/v1/auth/login/?username={user.username}&password=Correct-Horse-2026",
        {},
        format="json",
    )

    assert response.status_code == 400
    assert response.data["error"]["code"] == "VALIDATION_ERROR"


def test_auth_failures_never_log_or_echo_passwords_and_tokens(api_client, user, caplog, capsys):
    password_marker = "Never-Log-This-Password-2026"
    token_marker = "Never.Log.This.Token"

    login_response = api_client.post(
        "/api/v1/auth/login/",
        {"username": user.username, "password": password_marker},
        format="json",
    )
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token_marker}")
    token_response = api_client.get("/api/v1/auth/me/")

    captured = capsys.readouterr()
    evidence = "\n".join(
        [
            caplog.text,
            captured.out,
            captured.err,
            str(login_response.data),
            str(token_response.data),
        ]
    )
    assert password_marker not in evidence
    assert token_marker not in evidence

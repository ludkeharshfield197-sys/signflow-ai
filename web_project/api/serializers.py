import re

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from user.models import SysUser


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=100, trim_whitespace=True)
    password = serializers.CharField(max_length=128, trim_whitespace=False, write_only=True)


class RegisterSerializer(serializers.Serializer):
    username = serializers.RegexField(
        r"^[A-Za-z0-9_.-]{3,32}$",
        max_length=32,
        error_messages={"invalid": "账号仅支持字母、数字、点、横线和下划线。"},
    )
    email = serializers.EmailField(required=False, allow_blank=True, max_length=100)
    password = serializers.CharField(
        min_length=10, max_length=128, write_only=True, trim_whitespace=False
    )
    confirmPassword = serializers.CharField(max_length=128, write_only=True, trim_whitespace=False)

    def validate_username(self, value):
        if SysUser.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("该账号已存在。")
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["confirmPassword"]:
            raise serializers.ValidationError({"confirmPassword": "两次输入的密码不一致。"})
        if not re.search(r"[A-Za-z]", attrs["password"]) or not re.search(r"\d", attrs["password"]):
            raise serializers.ValidationError({"password": "密码必须同时包含字母和数字。"})
        candidate = SysUser(username=attrs["username"], email=attrs.get("email") or None)
        try:
            validate_password(attrs["password"], user=candidate)
        except DjangoValidationError as exc:
            raise serializers.ValidationError({"password": list(exc.messages)}) from exc
        return attrs


class SafeUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = SysUser
        fields = ("id", "username", "avatar", "email")
        read_only_fields = fields

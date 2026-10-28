from pathlib import Path

from django.core.exceptions import ImproperlyConfigured

from .base import *


def require_env(name):
    value = env(name)
    if value in (None, ""):
        raise ImproperlyConfigured(f"{name} must be set in production.")
    return value


def require_list(name):
    values = env_list(name)
    if not values:
        raise ImproperlyConfigured(f"{name} must contain at least one value in production.")
    return values


SECRET_KEY = require_env("DJANGO_SECRET_KEY")
if SECRET_KEY.startswith("django-insecure") or len(SECRET_KEY) < 50:
    raise ImproperlyConfigured(
        "DJANGO_SECRET_KEY must be a strong value of at least 50 characters."
    )

DEBUG = False
ALLOWED_HOSTS = require_list("DJANGO_ALLOWED_HOSTS")
CORS_ALLOWED_ORIGINS = require_list("CORS_ALLOWED_ORIGINS")
CSRF_TRUSTED_ORIGINS = require_list("CSRF_TRUSTED_ORIGINS")
CORS_ALLOW_ALL_ORIGINS = False

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": require_env("DB_NAME"),
        "USER": require_env("DB_USER"),
        "PASSWORD": require_env("DB_PASSWORD"),
        "HOST": require_env("DB_HOST"),
        "PORT": require_env("DB_PORT"),
        "OPTIONS": {
            "charset": "utf8mb4",
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
        },
        "CONN_MAX_AGE": env_int("DB_CONN_MAX_AGE", 60),
    }
}

MODELS_ROOT = Path(require_env("MODEL_STORAGE_ROOT")).resolve()
MEDIA_STORAGE_BACKEND = require_env("MEDIA_STORAGE_BACKEND").lower()
if MEDIA_STORAGE_BACKEND != "s3":
    raise ImproperlyConfigured("MEDIA_STORAGE_BACKEND must be 's3' in production.")

AWS_STORAGE_BUCKET_NAME = require_env("MEDIA_STORAGE_BUCKET")
AWS_S3_ENDPOINT_URL = require_env("MEDIA_STORAGE_ENDPOINT")
AWS_ACCESS_KEY_ID = require_env("MEDIA_STORAGE_ACCESS_KEY")
AWS_SECRET_ACCESS_KEY = require_env("MEDIA_STORAGE_SECRET_KEY")
AWS_S3_REGION_NAME = env("MEDIA_STORAGE_REGION", "us-east-1")
AWS_S3_ADDRESSING_STYLE = env("MEDIA_STORAGE_ADDRESSING_STYLE", "path")
AWS_QUERYSTRING_AUTH = True
AWS_QUERYSTRING_EXPIRE = env_int("MEDIA_SIGNED_URL_TTL", 300)
AWS_DEFAULT_ACL = None
AWS_S3_FILE_OVERWRITE = False

STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "bucket_name": AWS_STORAGE_BUCKET_NAME,
            "endpoint_url": AWS_S3_ENDPOINT_URL,
            "access_key": AWS_ACCESS_KEY_ID,
            "secret_key": AWS_SECRET_ACCESS_KEY,
            "region_name": AWS_S3_REGION_NAME,
            "addressing_style": AWS_S3_ADDRESSING_STYLE,
            "querystring_auth": True,
            "querystring_expire": AWS_QUERYSTRING_EXPIRE,
        },
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.ManifestStaticFilesStorage",
    },
}

SIMPLE_JWT["SIGNING_KEY"] = SECRET_KEY
AUTH_COOKIE_SECURE = True
AUTH_COOKIE_SAMESITE = "Strict"
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = False
SECURE_SSL_REDIRECT = env_bool("DJANGO_SECURE_SSL_REDIRECT", True)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_HSTS_SECONDS = env_int("DJANGO_HSTS_SECONDS", 3_600)
SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool("DJANGO_HSTS_INCLUDE_SUBDOMAINS", False)
SECURE_HSTS_PRELOAD = env_bool("DJANGO_HSTS_PRELOAD", False)
SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin"

ENABLE_LEGACY_ENDPOINTS = False

import os
from datetime import timedelta
from pathlib import Path

# Production and test processes must never mutate their Python environment at runtime.
os.environ.setdefault("YOLO_AUTOINSTALL", "false")

BASE_DIR = Path(__file__).resolve().parents[2]


def env(name, default=None):
    return os.getenv(name, default)


def env_bool(name, default=False):
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def env_int(name, default):
    value = os.getenv(name)
    return int(value) if value not in (None, "") else default


def env_list(name, default=None):
    value = os.getenv(name)
    if value is None:
        return list(default or [])
    return [item.strip() for item in value.split(",") if item.strip()]


def database_from_environment():
    engine = env("DB_ENGINE", "sqlite").lower()
    if engine in {"sqlite", "sqlite3"}:
        return {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": env("DB_NAME", str(BASE_DIR / "local.sqlite3")),
        }
    return {
        "ENGINE": "django.db.backends.mysql",
        "NAME": env("DB_NAME", ""),
        "USER": env("DB_USER", ""),
        "PASSWORD": env("DB_PASSWORD", ""),
        "HOST": env("DB_HOST", "127.0.0.1"),
        "PORT": env("DB_PORT", "3306"),
        "OPTIONS": {
            "charset": "utf8mb4",
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
        },
        "CONN_MAX_AGE": env_int("DB_CONN_MAX_AGE", 60),
    }


SECRET_KEY = ""
DEBUG = False
ALLOWED_HOSTS = []

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
    "channels",
    "user.apps.UserConfig",
    "role.apps.RoleConfig",
    "menu.apps.MenuConfig",
    "modelYolo.apps.ModelYoloConfig",
    "ImageModel.apps.ImagemodelConfig",
    "CameraModel.apps.CameramodelConfig",
    "videoModel.apps.VideomodelConfig",
    "Agent.apps.AgentConfig",
    "detections.apps.DetectionsConfig",
    "health.apps.HealthConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "api.middleware.RequestIdMiddleware",
    "web_project.logging.StructuredRequestLoggingMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "api.middleware.SecurityHeadersMiddleware",
]

ROOT_URLCONF = "web_project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "web_project.wsgi.application"
ASGI_APPLICATION = "web_project.asgi.application"

DATABASES = {"default": database_from_environment()}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 10},
    },
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "zh-hans"
TIME_ZONE = "Asia/Shanghai"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = Path(env("MEDIA_STORAGE_ROOT", str(BASE_DIR / "media"))).resolve()
MODELS_ROOT = Path(env("MODEL_STORAGE_ROOT", str(BASE_DIR / "model"))).resolve()
MODELS_URL = "/model/"
MODEL_CACHE_SIZE = env_int("MODEL_CACHE_SIZE", 2)
MODEL_DEPLOYMENT_LABEL = env("MODEL_DEPLOYMENT_LABEL", "异步推理服务")
MODEL_EVALUATION_DATASET = env("MODEL_EVALUATION_DATASET", "")
MODEL_EVALUATION_SAMPLE_COUNT = env("MODEL_EVALUATION_SAMPLE_COUNT", "")
MODEL_EVALUATED_AT = env("MODEL_EVALUATED_AT", "")
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

DATA_UPLOAD_MAX_MEMORY_SIZE = env_int("DATA_UPLOAD_MAX_MEMORY_SIZE", 52_428_800)
FILE_UPLOAD_MAX_MEMORY_SIZE = env_int("FILE_UPLOAD_MAX_MEMORY_SIZE", 10_485_760)
FILE_UPLOAD_PERMISSIONS = 0o640
DETECTION_IMAGE_MAX_BYTES = env_int("DETECTION_IMAGE_MAX_BYTES", 20 * 1024 * 1024)
DETECTION_VIDEO_MAX_BYTES = env_int("DETECTION_VIDEO_MAX_BYTES", 500 * 1024 * 1024)
DETECTION_RETENTION_DAYS = env_int("DETECTION_RETENTION_DAYS", 30)
DETECTION_AUTO_DISPATCH = env_bool("DETECTION_AUTO_DISPATCH", True)

CORS_ALLOWED_ORIGINS = env_list("CORS_ALLOWED_ORIGINS")
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-request-id",
    "x-requested-with",
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ["api.authentication.SysUserJWTAuthentication"],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "EXCEPTION_HANDLER": "api.exceptions.api_exception_handler",
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": env("API_ANON_RATE", "60/min"),
        "user": env("API_USER_RATE", "600/min"),
        "auth": env("API_AUTH_RATE", "10/min"),
    },
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=env_int("JWT_ACCESS_MINUTES", 15)),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=env_int("JWT_REFRESH_DAYS", 7)),
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
}

AUTH_REFRESH_COOKIE = env("AUTH_REFRESH_COOKIE", "signflow_refresh")
AUTH_COOKIE_SECURE = False
AUTH_COOKIE_SAMESITE = "Lax"

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "signflow-local",
    }
}

REDIS_URL = env("REDIS_URL", "")
CACHE_URL = env("CACHE_URL", REDIS_URL)
if CACHE_URL:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": CACHE_URL,
        }
    }
if REDIS_URL:
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {"hosts": [REDIS_URL]},
        }
    }
else:
    CHANNEL_LAYERS = {"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}}

CELERY_BROKER_URL = env("CELERY_BROKER_URL", REDIS_URL or "redis://127.0.0.1:6379/0")
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND", REDIS_URL or "redis://127.0.0.1:6379/1")
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_ACKS_LATE = True
CELERY_TASK_REJECT_ON_WORKER_LOST = True
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_TASK_ALWAYS_EAGER = env_bool("CELERY_TASK_ALWAYS_EAGER", False)
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_DETECTION_QUEUE = env("CELERY_DETECTION_QUEUE", "detections")
CELERY_TASK_EXPIRES_SECONDS = env_int("CELERY_TASK_EXPIRES_SECONDS", 900)

ENABLE_LEGACY_ENDPOINTS = env_bool("ENABLE_LEGACY_ENDPOINTS", False)
ENABLE_CAMERA_WEBSOCKET = env_bool("ENABLE_CAMERA_WEBSOCKET", False)
CAMERA_MAX_FPS = env_int("CAMERA_MAX_FPS", 5)
CAMERA_MAX_MESSAGE_BYTES = env_int("CAMERA_MAX_MESSAGE_BYTES", 2 * 1024 * 1024)
CAMERA_MAX_FRAME_BYTES = env_int("CAMERA_MAX_FRAME_BYTES", 1_500_000)
CAMERA_SESSION_SECONDS = env_int("CAMERA_SESSION_SECONDS", 300)
CAMERA_MAX_SESSIONS_PER_USER = env_int("CAMERA_MAX_SESSIONS_PER_USER", 2)
CAMERA_TICKET_SECONDS = env_int("CAMERA_TICKET_SECONDS", 60)

X_FRAME_OPTIONS = "DENY"
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": "web_project.logging.JsonFormatter",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
        },
    },
    "loggers": {
        "signflow": {
            "handlers": ["console"],
            "level": env("LOG_LEVEL", "INFO"),
            "propagate": False,
        },
        "django": {
            "handlers": ["console"],
            "level": env("DJANGO_LOG_LEVEL", "INFO"),
            "propagate": False,
        },
        "detections": {
            "handlers": ["console"],
            "level": env("LOG_LEVEL", "INFO"),
            "propagate": False,
        },
        "CameraModel": {
            "handlers": ["console"],
            "level": env("LOG_LEVEL", "INFO"),
            "propagate": False,
        },
    },
}

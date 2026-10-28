from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
SECRET_KEY = "test-only-signflow-secret-key"
DEBUG = False
ALLOWED_HOSTS = ["testserver", "localhost", "127.0.0.1"]

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "rest_framework",
    "user.apps.UserConfig",
    "role.apps.RoleConfig",
    "menu.apps.MenuConfig",
    "modelYolo.apps.ModelYoloConfig",
    "detections.apps.DetectionsConfig",
    "CameraModel.apps.CameramodelConfig",
    "health.apps.HealthConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "tests.urls"
TEMPLATES = []
USE_TZ = True
TIME_ZONE = "Asia/Shanghai"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / ".test.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = []
PASSWORD_HASHERS = ["django.contrib.auth.hashers.PBKDF2PasswordHasher"]

AUTH_REFRESH_COOKIE = "signflow_refresh"
AUTH_COOKIE_SECURE = False
AUTH_COOKIE_SAMESITE = "Lax"
DETECTION_IMAGE_MAX_BYTES = 20 * 1024 * 1024
DETECTION_VIDEO_MAX_BYTES = 500 * 1024 * 1024
DETECTION_RETENTION_DAYS = 30
DETECTION_AUTO_DISPATCH = False

REST_FRAMEWORK = {
    "EXCEPTION_HANDLER": "api.exceptions.api_exception_handler",
    "DEFAULT_THROTTLE_RATES": {"auth": "2/min"},
}

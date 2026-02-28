"""
Django settings for config project.
Production-ready configuration (Dev + Prod compatible)
"""

from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# ========================
# SECURITY
# ========================

# DEBUG 환경변수 기반 (기본값 False)
DEBUG = os.environ.get("DJANGO_DEBUG", "False") == "True"

# SECRET_KEY 처리
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")

if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = "dev-secret-key"
    else:
        raise RuntimeError("DJANGO_SECRET_KEY environment variable is not set")

ALLOWED_HOSTS = [
    "booksmakers.com",
    "www.booksmakers.com",
    "54.116.91.126",
    "43.201.76.182",
    "127.0.0.1",
    "localhost",
]

# HTTPS behind Nginx
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# 보안 헤더
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# HTTPS 강제 리다이렉트 (운영에서만 적용)
SECURE_SSL_REDIRECT = not DEBUG

# CSRF
CSRF_TRUSTED_ORIGINS = [
    "http://booksmakers.com",
    "http://www.booksmakers.com",
    "https://booksmakers.com",
    "https://www.booksmakers.com",
]

# 쿠키 보안 (운영에서만 True)
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

# ========================
# APPLICATIONS
# ========================

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "apps.cart",
    "apps.orders.apps.OrdersConfig",
    "apps.catalog",
    "users",
    "accounts",
]

# ========================
# MIDDLEWARE
# ========================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

# ========================
# TEMPLATES
# ========================

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.cart.context_processors.cart_count",
                "apps.catalog.context_processors.global_categories",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# ========================
# DATABASE
# ========================

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "booksmakers_dev",
        "USER": "booksmakers_user",
        "PASSWORD": "devpassword",
        "HOST": "127.0.0.1",
        "PORT": "5432",
    }
}

# ========================
# PASSWORD VALIDATION
# ========================

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ========================
# INTERNATIONALIZATION
# ========================

LANGUAGE_CODE = "ko-kr"
TIME_ZONE = "Asia/Seoul"
USE_I18N = True
USE_TZ = True

# ========================
# STATIC / MEDIA
# ========================

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

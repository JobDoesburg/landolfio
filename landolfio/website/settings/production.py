"""
The production settings.

These settings are to be used in deployment.
Also see https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/.
"""
import os

from .common import *  # pylint: disable=wildcard-import,unused-wildcard-import

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

SENTRY_DSN = os.environ.get("SENTRY_DSN", None)

if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        environment="production",
        traces_sample_rate=1.0,
        send_default_pii=True,
        _experiments={
            "profiles_sample_rate": 1.0,
        },
    )

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("LANDOLFIO_SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = os.environ.get("LANDOLFIO_ALLOWED_HOSTS", "").split(",")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB"),
        "USER": os.environ.get("POSTGRES_USER"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD"),
        "HOST": os.environ.get("POSTGRES_HOST"),
        "PORT": os.environ.get("POSTGRES_PORT"),
    }
}

STATIC_URL = os.environ.get("DJANGO_STATIC_URL")
MEDIA_URL = os.environ.get("DJANGO_MEDIA_URL")

STATIC_ROOT = os.environ.get("DJANGO_STATIC_ROOT")
MEDIA_ROOT = os.environ.get("DJANGO_MEDIA_ROOT")

DJANGO_DRF_FILEPOND_UPLOAD_TMP = os.path.join(MEDIA_ROOT, "filepond-temp-uploads")
DJANGO_DRF_FILEPOND_ALLOW_EXTERNAL_UPLOAD_DIR = True

# We do this in our reverse proxy, no need to do it here
SECURE_SSL_REDIRECT = False

SESSION_COOKIE_SECURE = True

CSRF_COOKIE_SECURE = True

# see: https://docs.djangoproject.com/en/4.0/ref/settings/#csrf-trusted-origins
CSRF_TRUSTED_ORIGINS = ["https://" + host for host in ALLOWED_HOSTS]

MONEYBIRD_WEBHOOK_SITE_DOMAIN = "https://" + ALLOWED_HOSTS[0]
BASE_URL = MONEYBIRD_WEBHOOK_SITE_DOMAIN

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{asctime} ({levelname}) {name}: {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "level": os.environ.get("DJANGO_LOG_LEVEL", "INFO"),
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "file": {
            "level": os.environ.get("DJANGO_LOG_LEVEL", "INFO"),
            "class": "logging.FileHandler",
            "formatter": "verbose",
            "filename": "/var/log/django.log",
        },
    },
    "root": {
        "handlers": ["console", "file"],
        "level": os.environ.get("DJANGO_LOG_LEVEL", "ERROR"),
    },
}


EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.environ.get("SMTP_HOST", None)
EMAIL_PORT = int(os.environ.get("SMTP_PORT", 0))
EMAIL_USE_TLS = os.environ.get("SMTP_USE_TLS", None) == "True"
EMAIL_USE_SSL = os.environ.get("SMTP_USE_SSL", None) == "True"
EMAIL_HOST_USER = os.environ.get("SMTP_USER", None)
EMAIL_HOST_PASSWORD = os.environ.get("SMTP_PASSWORD", None)

EMAIL_DEFAULT_SENDER = os.environ.get("SMTP_FROM", None)
DEFAULT_FROM_EMAIL = os.environ.get("SMTP_FROM_EMAIL", None)
SERVER_EMAIL = os.environ.get("SMTP_FROM", None)

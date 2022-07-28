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
    )

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("LANDOLFIO_SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = os.environ.get("LANDOLFIO_ALLOWED_HOSTS").split(",")

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

STATIC_ROOT = "/landolfio/static/"
STATIC_URL = "/static/"

MEDIA_ROOT = "/landolfio/media/"
MEDIA_URL = "/media/"

# We do this in our reverse proxy, no need to do it here
SECURE_SSL_REDIRECT = False

SESSION_COOKIE_SECURE = True

CSRF_COOKIE_SECURE = True

# see: https://docs.djangoproject.com/en/4.0/ref/settings/#csrf-trusted-origins
CSRF_TRUSTED_ORIGINS = ["https://" + host for host in ALLOWED_HOSTS]

MONEYBIRD_WEBHOOK_SITE_DOMAIN = "https://" + ALLOWED_HOSTS[0]

"""
The production settings.

These settings are to be used in deployment.
Also see https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/.
"""
import os

from .common import *  # pylint: disable=wildcard-import,unused-wildcard-import

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

# We do this in our reverse proxy, no need to do it here
SECURE_SSL_REDIRECT = False

SESSION_COOKIE_SECURE = True

CSRF_COOKIE_SECURE = True

# see: https://docs.djangoproject.com/en/4.0/ref/settings/#csrf-trusted-origins
CSRF_TRUSTED_ORIGINS = ["https://" + host for host in ALLOWED_HOSTS]

MONEYBIRD_ADMINISTRATION_ID = int(os.environ.get("MONEYBIRD_ADMINISTRATION_ID"))
MONEYBIRD_API_KEY = os.environ.get("MONEYBIRD_API_KEY")
MONEYBIRD_WEBHOOK_SITE_DOMAIN = "https://" + ALLOWED_HOSTS[0]

"""
The development settings.

These settings are unsuitable for production, but have some advantages while
developing.
"""
import os

from .common import *  # pylint: disable=wildcard-import,unused-wildcard-import


SECRET_KEY = "django-insecure-y%!#gz*&6n!av8zdlci#*x+w-!z&fkb)@se*pzoyk+2team_-r"

DEBUG = True

TEMPLATES[0]["OPTIONS"]["debug"] = True

INSTALLED_APPS += ["debug_toolbar"]

MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]
INTERNAL_IPS = [
    "127.0.0.1",
]

ALLOWED_HOSTS = []

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
EMAIL_DEFAULT_SENDER = "development@landolfio.localhost"

MONEYBIRD_WEBHOOK_SITE_DOMAIN = "http://localhost:8000"
BASE_URL = MONEYBIRD_WEBHOOK_SITE_DOMAIN


MEDIA_ROOT = BASE_DIR / "media"
MEDIA_URL = "/media/"

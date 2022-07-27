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
        "level": "DEBUG",
    },
}

MONEYBIRD_WEBHOOK_SITE_DOMAIN = "http://localhost:8000"

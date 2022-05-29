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

MONEYBIRD_ADMINISTRATION_ID = int(os.getenv("MONEYBIRD_ADMINISTRATION_ID", "0"))
MONEYBIRD_API_KEY = os.getenv("MONEYBIRD_API_KEY", "")
MONEYBIRD_SYNC_INTERVAL = int(os.getenv("MONEYBIRD_SYNC_INTERVAL", "5"))

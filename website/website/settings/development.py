"""
The development settings.

These settings are unsuitable for production, but have some advantages while
developing.
"""
import os

from .common import *  # pylint: disable=wildcard-import,unused-wildcard-import


SECRET_KEY = "django-insecure-y%!#gz*&6n!av8zdlci#*x+w-!z&fkb)@se*pzoyk+2team_-r"

DEBUG = True

ALLOWED_HOSTS = []

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

MONEYBIRD_ADMINISTRATION_ID = os.getenv("MONEYBIRD_ADMINISTRATION_ID", "")
MONEYBIRD_API_KEY = os.getenv("MONEYBIRD_API_KEY", "")

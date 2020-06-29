import os

from landolfio.settings.base import *  # noqa

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False


ALLOWED_HOSTS = ["landolfio.vofdoesburg.nl"]

SESSION_COOKIE_SECURE = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": os.environ.get("POSTGRES_HOST"),
        "PORT": int(os.environ.get("POSTGRES_PORT", 5432)),
        "NAME": os.environ.get("POSTGRES_NAME"),
        "USER": os.environ.get("POSTGRES_USER"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD"),
    }
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": "/landolfio/log/django.log",
        },
    },
    "loggers": {
        "": {"handlers": ["file"], "level": "DEBUG", "propagate": True,},  # noqa
    },  # noqa
}

if os.environ.get("DJANGO_EMAIL_HOST"):
    EMAIL_HOST = os.environ["DJANGO_EMAIL_HOST"]
    EMAIL_PORT = os.environ["DJANGO_EMAIL_PORT"]
    EMAIL_HOST_USER = os.environ.get("DJANGO_EMAIL_HOST_USER")
    EMAIL_HOST_PASSWORD = os.environ.get("DJANGO_EMAIL_HOST_PASSWORD")
    EMAIL_USE_TLS = os.environ.get("DJANGO_EMAIL_USE_TLS", False) == "True"
    EMAIL_USE_SSL = os.environ.get("DJANGO_EMAIL_USE_SSL", False) == "True"

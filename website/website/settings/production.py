"""
The production settings.

These settings are to be used in deployment.
Also see https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/.
"""
import os

from .common import *  # pylint: disable=wildcard-import,unused-wildcard-import


def config(key: str) -> str:
    """
    Get an environment variable, or throw an exception with a clear message.

    This function throws a KeyError exception if it cannot be found. It exists
    to make the error message of the error more descriptive.
    """
    try:
        return os.environ[key]
    except KeyError as err:
        error_message = f"{key} not found. Define it as an environment variable."
        raise KeyError(error_message) from err


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("LANDOLFIO_SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = config("LANDOLFIO_ALLOWED_HOSTS").split(",")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("POSTGRES_DB"),
        "USER": config("POSTGRES_USER"),
        "PASSWORD": config("POSTGRES_PASSWORD"),
        "HOST": config("POSTGRES_HOST"),
        "PORT": config("POSTGRES_PORT"),
    }
}

# We do this in our reverse proxy, no need to do it here
SECURE_SSL_REDIRECT = False

SESSION_COOKIE_SECURE = True

CSRF_COOKIE_SECURE = True

# see: https://docs.djangoproject.com/en/4.0/ref/settings/#csrf-trusted-origins
CSRF_TRUSTED_ORIGINS = ["https://" + host for host in ALLOWED_HOSTS]

MONEYBIRD_ADMINISTRATION_ID = config("MONEYBIRD_ADMINISTRATION_ID")
MONEYBIRD_API_KEY = config("MONEYBIRD_API_KEY")

"""
Development settings for the landolfio project
"""

import os

from landolfio.settings.base import *  # noqa

SECRET_KEY = "Q7H7CA#O4!pOZjcpR0m9aG58PZRY7h@g6k!AF4vyGk@HqkAavc"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "brief": {
            "format": "%(name)s %(levelname)s %(message)s"
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "brief",
        }
    },
    "loggers": {
        "django": {"handlers": ["console"], "level": "INFO", "propagate": False,},  # noqa
        "moneybird": {"handlers": ["console"], "level": "DEBUG", "propagate": False, },  # noqa
    },  # noqa
}

MONEYBIRD_API_TOKEN = os.environ.get("MONEYBIRD_API_TOKEN", 'cfc5e6f4dac55776889723c5dc6083fba4043f3e5cee8411b1a3afb6435a49d4')
MONEYBIRD_ADMINISTRATION_ID = os.environ.get("MONEYBIRD_ADMINISTRATION_ID", 293065149189719909)

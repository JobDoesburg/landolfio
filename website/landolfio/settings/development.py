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
    "handlers": {
        "console": {"level": "INFO", "class": "logging.StreamHandler",},  # noqa
    },  # noqa
    "loggers": {
        "": {"handlers": ["console"], "level": "INFO", "propagate": True,},  # noqa
    },  # noqa
}

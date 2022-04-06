"""
The test settings.

These settings are unsuitable for production, but have some advantages while testing.
"""
from .development import *  # pylint: disable=wildcard-import,unused-wildcard-import

DEFAULT_FILE_STORAGE = "inmemorystorage.InMemoryStorage"

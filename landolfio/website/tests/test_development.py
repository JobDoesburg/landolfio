"""Tests for Django development settings."""
from django.test import TestCase


class DevelopmentSettingsTest(TestCase):
    """Test the development settings."""

    def test_import(self):
        """Importing the development settings must not raise any exceptions."""
        # pylint: disable=import-outside-toplevel,unused-import,no-self-use
        from website.settings import development

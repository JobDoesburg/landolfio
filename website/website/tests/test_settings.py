"""Tests for Django settings."""
import os
from unittest import mock

from django.test import TestCase


class DevelopmentSettingsTest(TestCase):
    """Test the development settings."""

    def test_import(self):
        """Importing the development settings must not raise any exceptions."""
        # pylint: disable=import-outside-toplevel,unused-import,no-self-use
        from website.settings import development


MOCK_ENVIRONMENT_PRODUCTION = {
    "LANDOLFIO_SECRET_KEY": "myverysecretkey",
    "LANDOLFIO_ALLOWED_HOSTS": "landolfio.example.com, landolfio2.example.com",
    "POSTGRES_DB": "db",
    "POSTGRES_USER": "user",
    "POSTGRES_PASSWORD": "postgres_password",
    "POSTGRES_HOST": "database",
    "POSTGRES_PORT": "5432",
}


@mock.patch.dict(os.environ, MOCK_ENVIRONMENT_PRODUCTION, clear=True)
class ProductionSettingsTest(TestCase):
    """Test the production settings."""

    def test_debug_false(self):
        """The value DEBUG is set to False."""
        # pylint: disable=import-outside-toplevel
        from website.settings import production

        self.assertEqual(production.DEBUG, False)

    @mock.patch.dict(
        os.environ, {"LANDOLFIO_ALLOWED_HOSTS": "a.example.com,b.example.com"}
    )
    def test_allowed_hosts(self):
        """The ALLOWED_HOSTS are parsed correctly."""
        # pylint: disable=import-outside-toplevel
        from website.settings import production

        self.assertEqual(production.ALLOWED_HOSTS, ["a.example.com", "b.example.com"])

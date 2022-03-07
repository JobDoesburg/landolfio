"""Tests for Asgi."""
from django.test import RequestFactory
from django.test import TestCase
from django.urls import Resolver404

from .asgi import application


class AsgiTest(TestCase):
    """Test the Asynchronous Server Gateway Interface."""

    def test_handles_request(self):
        """The ASGI can resolve a request."""
        request = RequestFactory().get("/")

        with self.assertRaises(Resolver404):
            application.resolve_request(request)

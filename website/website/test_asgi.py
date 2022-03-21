"""Tests for Asgi."""
from django.test import RequestFactory
from django.test import TestCase

from .asgi import application


class AsgiTest(TestCase):
    """Test the Asynchronous Server Gateway Interface."""

    @staticmethod
    def test_handles_request():
        """The ASGI can resolve a request without raising an exception."""
        request = RequestFactory().get("/")
        application.resolve_request(request)

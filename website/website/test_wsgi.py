"""Tests for Wsgi."""
from django.test import RequestFactory
from django.test import TestCase
from django.urls import Resolver404

from .wsgi import application


class WsgiTest(TestCase):
    """Test the Web Server Gateway Interface."""

    def test_handles_request(self):
        """The WSGI can handle a request."""
        request = RequestFactory().get("/")

        with self.assertRaises(Resolver404):
            application.resolve_request(request)

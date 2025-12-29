"""Tests for Wsgi."""

from django.test import RequestFactory, TestCase

from website.wsgi import application


class WsgiTest(TestCase):
    """Test the Web Server Gateway Interface."""

    @staticmethod
    def test_handles_request():
        """The WSGI can handle a request without raising an exception."""
        request = RequestFactory().get("/")
        application.resolve_request(request)

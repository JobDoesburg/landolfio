"""Test the Moneybird Administrations."""
from django.test import TestCase

from .administration import _build_url as build_url
from .administration import Administration


class ErrorTest(TestCase):
    """Test the Administration errors."""

    @staticmethod
    def test_construction():
        """The construction of an error must not fail."""
        Administration.NotFound(404, "Resource not found")

    @staticmethod
    def test_construction_without_description():
        """The construction of an error without a description must not fail."""
        Administration.ServerError(500)


class BuildURLTest(TestCase):
    """Test the function to build URLs."""

    def test_one_file_without_leading_slash(self):
        """If we build a URL with the path 'test', the  must be correct."""
        url = build_url(3, "test")
        self.assertEqual(url, "https://moneybird.com/api/v2/3/test.json")

    def test_one_file_with_leading_slash(self):
        """
        Test a simple path with a leading slash.

        If we build a URL with the path '/test' (note the leading slash), we expect a
        failure.
        """
        with self.assertRaises(Administration.InvalidResourcePath):
            build_url(3, "/test")

    def test_path_without_leading_slash(self):
        """If we build a URL with a longer path, the URL must be correct."""
        url = build_url(4, "documents/purchase_invoices/synchronization")
        self.assertEqual(
            url,
            "https://moneybird.com/api/v2/4/documents/purchase_invoices"
            "/synchronization.json",
        )

    def test_path_with_leading_slash(self):
        """
        Test building a path with a leading slash.

        If we build a URL with a path that has a leading slash, we expect a failure.
        """
        with self.assertRaises(Administration.InvalidResourcePath):
            build_url(4, "/documents/purchase_invoices/synchronization")

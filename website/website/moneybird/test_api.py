from django.test import TestCase

from .api import _build_url as build_url


class TestBuildURL(TestCase):
    """Test the function to build URLs."""

    def test_one_file(self):
        """Building a URL with only the path 'test' must create a valid URL."""
        url = build_url(3, "test")
        self.assertEqual(url, "https://moneybird.com/api/v2/3/test.json")

    def test_path(self):
        """Building a URL with a path must create a valid URL."""
        url = build_url(3, "documents/purchase_invoices/synchronization")
        self.assertEqual(
            url,
            "https://moneybird.com/api/v2/3/documents/purchase_invoices/synchronization.json",
        )

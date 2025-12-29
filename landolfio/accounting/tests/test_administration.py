"""Test the Moneybird Administrations."""

from django.test import TestCase

from website.accounting.moneybird import Administration
from website.accounting.moneybird.administration import _build_url as build_url


class MockAdministration(Administration):
    """Mock version of a MoneyBird administration."""

    def __init__(self, documents: dict[str, list[dict]], max_requests: int = math.inf):
        """Initialize a new MockAdministration."""
        super().__init__()
        self.documents = documents
        self.max_requests = max_requests
        self.total_requests = 0

    def reset_total_requests(self):
        """Reset the number of requests made so far."""
        self.total_requests = 0

    def get(self, resource_path: str):
        """Mock a GET request for the Moneybird Administration."""
        if self.total_requests >= self.max_requests:
            raise self.Throttled(429, "Too many requests")
        self.total_requests += 1

        if resource_path.endswith("/synchronization"):
            document_path = resource_path.removesuffix("/synchronization")
            documents_kind = (
                self.documents[document_path]
                if document_path in self.documents
                else [].copy()
            )

            return [
                {"id": doc["id"], "version": doc["version"]} for doc in documents_kind
            ]

        raise self.NotFound(404, f"Could not find a resource at path {resource_path}")

    def post(self, resource_path: str, data: dict):
        """Mock a POST request for the Moneybird Administration."""
        if self.total_requests >= self.max_requests:
            raise self.Throttled(429, "Too many requests")
        self.total_requests += 1

        if resource_path.endswith("/synchronization"):
            document_path = resource_path.removesuffix("/synchronization")
            if document_path in self.documents:
                documents_kind = self.documents[document_path]
            else:
                documents_kind = [].copy()

            ids = data["ids"]
            return filter(lambda doc: doc["id"] in ids, documents_kind)

        raise self.NotFound(404, f"Could not find a resource at path {resource_path}")


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

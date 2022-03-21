"""Test the MoneyBirdWrapper."""
from django.test import TestCase

from .api import Administration
from .wrapper import _get_changes_from_api as get_changes_from_api
from .wrapper import Diff


class MockAdministration(Administration):
    """Mock version of the MoneyBird API."""

    def __init__(self, documents):
        """Initialize a new MockMoneyBird."""
        super().__init__()
        self.documents = documents

    def get(self, resource_path: str):
        """Mock a GET request for the Moneybird API."""
        parts = resource_path.split("/")

        # Mock a GET request for a /documents/* resource path
        if (
            len(parts) == 3
            and parts[0] == "documents"
            and parts[2] == "synchronization"
        ):
            documents_kind = (
                self.documents[parts[1]] if parts[1] in self.documents else []
            )

            return [
                {"id": doc["id"], "version": doc["version"]} for doc in documents_kind
            ]

        raise self.NotFound

    def post(self, resource_path: str, data: dict):
        """Mock a POST request for the Moneybird API."""
        path = resource_path.split("/")
        if (
            len(path) == 3
            and path[0] == "documents"
            and path[1] in self.documents
            and path[2] == "synchronization"
        ):
            documents_kind = self.documents[path[1]]
            ids = data["ids"]
            return filter(lambda doc: doc["id"] in ids, documents_kind)

        # Incorrect path was used
        raise self.NotFound


class WrapperTest(TestCase):
    """Tests for the MoneyBird wrapper."""

    def test_load_purchase_invoices(self):
        """If we request the changes without a tag then we must get all changes."""
        documents = {
            "purchase_invoices": [{"id": "1", "version": 3}, {"id": "2", "version": 7}]
        }

        api = MockAdministration(documents)

        _tag, changes = get_changes_from_api(api)
        self.assertEqual(
            changes["purchase_invoices"], Diff(added=documents["purchase_invoices"])
        )

    def test_tag_usage(self):
        """
        Test the usage of a tag.

        If we request changes and use the returned tag to get new changes then the
        difference must be empty.
        """
        documents = {"receipts": [{"id": "1", "version": 3}, {"id": "2", "version": 7}]}
        api = MockAdministration(documents)

        tag1, _changes1 = get_changes_from_api(api)
        _tag2, changes2 = get_changes_from_api(api, tag=tag1)

        self.assertEqual(changes2["receipts"], Diff())

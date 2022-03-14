"""Test the MoneyBirdWrapper."""
import unittest

from .moneybird_wrapper import Diff
from .moneybird_wrapper import MoneyBirdApiWrapper


class MoneyBirdMock:
    """Mock version of the MoneyBird API."""

    # pylint: disable=too-few-public-methods

    def __init__(self, documents):
        """Initialize a new MoneyBirdMock."""
        self.documents = documents

    def get(self, resource_path: str, administration_id: int = None):
        """Mock a GET request for the Moneybird API."""
        # pylint: disable=unused-argument
        if resource_path == "administrations":
            return [{"id": "0"}]

        path = resource_path.split("/")

        if len(path) == 3 and path[0] == "documents" and path[2] == "synchronization":
            documents_kind = (
                self.documents[path[1]] if path[1] in self.documents else []
            )

            return [
                {"id": doc["id"], "version": doc["version"]} for doc in documents_kind
            ]

        # Incorrect path was used
        raise MoneyBirdMock.NotFound

    def post(self, resource_path: str, data: dict, administration_id: int = None):
        """Mock a POST request for the Moneybird API."""
        # pylint: disable=unused-argument

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
        raise MoneyBirdMock.NotFound

    class NotFound(Exception):
        """Exception for requests to non-existing resource paths."""


class MoneybirdWrapperTest(unittest.TestCase):
    """Class to test the MoneyBirdWrapper."""

    def test_load_purchase_invoices(self):
        """If we request the changes without a tag then we must get all changes."""
        documents = {
            "purchase_invoices": [{"id": "1", "version": 3}, {"id": "2", "version": 7}]
        }
        wrapper = MoneyBirdApiWrapper(MoneyBirdMock(documents))

        _tag, changes = wrapper.get_changes()
        self.assertEqual(
            changes["purchase_invoices"], Diff(added=documents["purchase_invoices"])
        )

    def test_tag_usage(self):
        """If we request changes and use the returned tag to get new changes then the difference must be empty."""
        documents = {"receipts": [{"id": "1", "version": 3}, {"id": "2", "version": 7}]}
        wrapper = MoneyBirdApiWrapper(MoneyBirdMock(documents))

        tag1, _changes1 = wrapper.get_changes()
        _tag2, changes2 = wrapper.get_changes(tag1)

        self.assertEqual(changes2["receipts"], Diff())

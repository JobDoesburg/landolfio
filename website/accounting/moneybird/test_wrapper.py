"""Test the MoneyBirdWrapper."""
from django.test import TestCase

from .api import MockAdministration
from .wrapper import Diff
from .wrapper import get_changes_from_api


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

    def test_remove(self):
        """
        Test requesting changes when documents are removed.

        If we request changes with a tag, and documents were removed on the remote,
        then those documents must be included in the diff as removed.
        """
        documents = {
            "purchase_invoices": [{"id": "1", "version": 3}, {"id": "2", "version": 7}]
        }

        api = MockAdministration(documents)

        tag1, _changes1 = get_changes_from_api(api)

        # remove documents
        ids_removed = [doc["id"] for doc in documents["purchase_invoices"]]
        api.documents.clear()

        _tag2, changes2 = get_changes_from_api(api, tag1)

        self.assertEqual(
            sorted(changes2["purchase_invoices"].removed), sorted(ids_removed)
        )

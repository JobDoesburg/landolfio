"""Test the sync_database module."""

from django.test import TestCase
from inmemorystorage import InMemoryStorage

from .. import sync_database as ud
from ..models import Document
from ..moneybird import DocKind, MockAdministration


class TagStorageTest(TestCase):
    """Test loading and saving of a tag."""

    # pylint: disable=protected-access

    @staticmethod
    def test_save():
        """
        Test saving a tag.

        If a correct tag is saved, then no exceptions should be raised.
        """
        ud._save_tag_to_storage(b"test tag", InMemoryStorage())

    def test_load_non_existing(self):
        """
        Test loading a tag when no tag exists.

        If the tag is requested, but no tag exists, the load_tag function must return
        None.
        """
        self.assertIsNone(ud._load_tag_from_storage(InMemoryStorage()))

    def test_save_non_bytes(self):
        """
        Test saving a tag which is not of type bytes.

        If a tag is saved, and it is not of type bytes, then an exception must be
        raised.
        """
        with self.assertRaises(AssertionError):
            ud._save_tag_to_storage("test tag", InMemoryStorage())

    def test_save_and_load(self):
        """
        Test saving a tag and then loading it.

        If a tag T1 is saved, and then a tag T2 is loaded, T1 must be equal to T2.
        """
        storage = InMemoryStorage()
        tag = b"sample tag"
        ud._save_tag_to_storage(tag, storage)
        self.assertEqual(tag, ud._load_tag_from_storage(storage))

    def test_save_twice_and_load(self):
        """
        Test overwriting a tag.

        If a tag T1 is saved, and then a tag T2 is saved, then loading a tag must
        give tag T2.
        """
        storage = InMemoryStorage()
        tag1 = b"sample tag 1"
        tag2 = b"sample tag 2"
        ud._save_tag_to_storage(tag1, storage)
        ud._save_tag_to_storage(tag2, storage)
        self.assertEqual(tag2, ud._load_tag_from_storage(storage))


class TestFindAssetID(TestCase):
    """Test the find_asset_id_from_description function."""

    # pylint: disable=protected-access

    def test_empty(self):
        """If the description is empty, no ID must be found in it."""
        self.assertIsNone(ud._find_asset_id_from_description(""))

    def test_full(self):
        """If the description contains only an ID, that ID must be found."""
        asset_id = "testid"
        description = f"[{asset_id}]"

        self.assertEqual(asset_id, ud._find_asset_id_from_description(description))

    def test_more_than_one(self):
        """If the description contains more than one ID, the first ID must be found."""
        asset_id = "testid"
        description = f"[{asset_id}][a][b][c]"

        self.assertEqual(asset_id, ud._find_asset_id_from_description(description))

    def test_id_surrounded_with_spaces(self):
        """
        Test using an ID with spaces.

        If the description contains an ID that is surrounded by spaces, the spaces
        must be ignored.
        """
        asset_id = "testid"
        description = f"[   {asset_id}     ]"

        self.assertEqual(asset_id, ud._find_asset_id_from_description(description))

    def test_in_sentence(self):
        """
        If the description is normal sentence with an ID in it, the ID must be found.
        """
        asset_id = "testid"
        description = f"The id is [{asset_id}]."

        self.assertEqual(asset_id, ud._find_asset_id_from_description(description))

    def test_empty_brackets(self):
        """
        If the description contains just '[]' then no ID must be found.
        """
        description = "[]"

        self.assertIsNone(ud._find_asset_id_from_description(description))

    def test_nested(self):
        """
        Test with nested brackets.

        If the description contains exactly one ID in nested brackets, then that ID
        must be found.
        """
        asset_id = "test"
        description = f"[[{asset_id}]]"

        self.assertEqual(asset_id, ud._find_asset_id_from_description(description))

    def test_over_lines(self):
        """
        Test with an invalid ID.

        If the description only contains something looking like an ID but split over
        lines, then no ID must be found.
        """
        description = "[t\nest]"

        self.assertIsNone(ud._find_asset_id_from_description(description))

    def test_multiple_lines(self):
        """
        Test with a multiline-description.

        If the description contains multiple lines of which only the second line
        contains the ID, that ID must be found.
        """
        asset_id = "test_id"
        description = f"This is a sentence.\nThis is an [{asset_id}]."

        self.assertEqual(asset_id, ud._find_asset_id_from_description(description))


class SyncDatabaseTest(TestCase):
    """Test the sync_database function."""

    # pylint: disable=protected-access

    def test_empty_remote(self):
        """
        Test updating from an empty remote administration.

        If the database is synchronized to an empty remote, afterwards the database must
        not contain any documents.
        """
        storage = InMemoryStorage()
        documents = {}
        adm = MockAdministration(documents)
        ud._sync_db_from_adm(adm, storage)

        self.assertEqual(
            Document.objects.count(),
            0,
            "There must be no documents after updating with an empty remote.",
        )

    def test_remote_with_one_purchase_invoice(self):
        """
        Test updating from a remote with exactly one document.

        If the database is synchronized to a remote with exactly one document,
        afterwards the database must that document and only that document.
        """
        invoice_id = 1
        invoice_version = 3
        invoice = {
            "id": str(invoice_id),
            "administration_id": "5",
            "version": invoice_version,
            "details": [
                {
                    "description": "document line 1\n",
                    "ledger_account_id": 10,
                    "total_price_excl_tax_with_discount_base": 100.0,
                },
                {
                    "description": "document line 2\n",
                    "ledger_account_id": 5,
                    "total_price_excl_tax_with_discount_base": 50.0,
                },
            ],
        }

        documents = {DocKind.PURCHASE_INVOICE.adm_path: [invoice]}

        adm = MockAdministration(documents)
        storage = InMemoryStorage()
        ud._sync_db_from_adm(adm, storage)

        self.assertEqual(Document.objects.count(), 1)

        document = Document.objects.first()
        self.assertEqual(document.moneybird_id, invoice_id)
        self.assertEqual(document.kind, DocKind.PURCHASE_INVOICE)
        self.assertEqual(document.moneybird_json, invoice)

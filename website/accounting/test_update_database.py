"""Test the update_database module."""
from django.core.files.storage import DefaultStorage
from django.test import TestCase

from . import update_database as ud
from .models import Document
from .moneybird import MockAdministration


class TagStorageTest(TestCase):
    """Test loading and saving of a tag."""

    # pylint: disable=protected-access

    def setUp(self) -> None:
        """
        Reset the storage before each test.

        This assumes that the non-persistent in-memory storage is used.
        """
        ud.default_storage = DefaultStorage()

    @staticmethod
    def test_save():
        """
        Test saving a tag.

        If a correct tag is saved, then no exceptions should be raised.
        """
        ud._save_tag_to_storage(b"test tag")

    def test_load_non_existing(self):
        """
        Test loading a tag when no tag exists.

        If the tag is requested, but no tag exists, the load_tag function must return
        None.
        """
        self.assertIsNone(ud._load_tag_from_storage())

    def test_save_non_bytes(self):
        """
        Test saving a tag which is not of type bytes.

        If a tag is saved, and it is not of type bytes, then an exception must be
        raised.
        """
        with self.assertRaises(AssertionError):
            ud._save_tag_to_storage("test tag")

    def test_save_and_load(self):
        """
        Test saving a tag and then loading it.

        If a tag T1 is saved, and then a tag T2 is loaded, T1 must be equal to T2.
        """
        tag = b"sample tag"
        ud._save_tag_to_storage(tag)
        self.assertEqual(tag, ud._load_tag_from_storage())

    def test_save_twice_and_load(self):
        """
        Test overwriting a tag.

        If a tag T1 is saved, and then a tag T2 is saved, then loading a tag must
        give tag T2.
        """
        tag1 = b"sample tag 1"
        tag2 = b"sample tag 2"
        ud._save_tag_to_storage(tag1)
        ud._save_tag_to_storage(tag2)
        self.assertEqual(tag2, ud._load_tag_from_storage())


class UpdateDatabaseTest(TestCase):
    """Test the update_database function."""

    # pylint: disable=protected-access

    def setUp(self) -> None:
        """
        Reset the storage before each test.

        This assumes that the non-persistent in-memory storage is used.
        """
        ud.default_storage = DefaultStorage()

    def test_empty_remote(self):
        """
        Test updating from an empty remote administration.

        If the database is updated from an empty remote, afterwards the database must
        not contain any documents.
        """
        documents = {}
        api = MockAdministration(documents)
        ud._update_db_from_api(api)

        self.assertEqual(
            Document.objects.count(),
            0,
            "There must be no documents after updating with an empty remote.",
        )

    def test_remote_with_one_purchase_invoice(self):
        """
        Test updating from a remote with exactly one document.

        If the database is updated from a remote with exactly one document,
        afterwards the database must that document and only that document.
        """
        invoice_id = 1
        invoice_version = 3
        invoice = {"id": str(invoice_id), "version": invoice_version}

        documents = {"purchase_invoices": [invoice]}
        api = MockAdministration(documents)
        ud._update_db_from_api(api)

        self.assertEqual(Document.objects.count(), 1)

        document = Document.objects.first()
        self.assertEqual(document.id_MB, invoice_id)
        self.assertEqual(document.json_MB, invoice)

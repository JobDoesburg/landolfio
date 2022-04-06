"""Test the update_database module."""
from django.test import TestCase

from . import update_database as ud


class TagStorageTest(TestCase):
    # pylint: disable=protected-access
    """Test loading and saving of a tag."""

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


class UpdateDatabaseTest(TestCase):
    """Test the update_database function."""

"""Test the get_changes module."""
from django.test import TestCase

from .administration import MockAdministration
from .get_changes import _chunk as chunk
from .get_changes import Diff
from .get_changes import DocKind
from .get_changes import get_administration_changes


class DocKindTest(TestCase):
    """Test the DocKind enum."""

    def test_all_kinds_have_a_path(self):
        """Each DocKind must have a path."""
        for kind in DocKind:
            self.assertIsNotNone(kind.path)

    def test_all_kinds_have_a_human_readable_name(self):
        """Each DocKind must have a human readable name."""
        for kind in DocKind:
            self.assertIsNotNone(kind.human_readable_name)


class ChunkTest(TestCase):
    """Test the chunk function."""

    def test_empty(self):
        """Chunking the empty list must yield no chunks."""
        self.assertListEqual(list(chunk([], 10)), [])

    def test_one(self):
        """Chunking a unary list must yield one chunk with that list."""
        self.assertListEqual(list(chunk(["foo"], 10)), [["foo"]])

    def test_one_less(self):
        """
        Test chunking with a list smaller than the chunk size.

        Chunking a list smaller than the chunk size must yield one chunk with only
        that list.
        """
        self.assertListEqual(list(chunk(["foo", "bar"], 3)), [["foo", "bar"]])

    def test_exact(self):
        """
        Test chunking a list of exactly the chunk size.

        Chunking a list with the length being exactly the chunk size must return one
        chunk with exactly that list.
        """
        self.assertListEqual(
            list(chunk(["foo", "bar", "baz"], 3)), [["foo", "bar", "baz"]]
        )

    def test_one_more(self):
        """
        Test chunking a list that is larger than the chunk size.

        Chunking a list with the length being larger than the chunk size must return
        multiple chunks.
        """
        self.assertListEqual(
            list(chunk(["foo", "bar", "baz", "qux"], 3)),
            [["foo", "bar", "baz"], ["qux"]],
        )


class GetChangesTest(TestCase):
    """Tests for the code responsible for getting changes from an administration."""

    def assertDiffEqual(self, a: Diff, b: Diff) -> None:
        # pylint: disable=invalid-name
        """Assert that two Diffs are identical."""
        self.assertCountEqual(a.added, b.added)
        self.assertCountEqual(a.changed, b.changed)
        self.assertCountEqual(a.removed, b.removed)

    def test_load_purchase_invoices(self):
        """If we request the changes without a tag then we must get all changes."""
        documents = {
            DocKind.PURCHASE_INVOICE.path: [
                {"id": "1", "version": 3},
                {"id": "2", "version": 7},
            ]
        }

        adm = MockAdministration(documents)

        _tag, changes = get_administration_changes(adm)

        self.assertDiffEqual(
            changes[DocKind.PURCHASE_INVOICE],
            Diff(added=documents[DocKind.PURCHASE_INVOICE.path]),
        )

    def test_tag_usage(self):
        """
        Test the usage of a tag.

        If we request changes and use the returned tag to get new changes then the
        difference must be empty.
        """
        documents = {
            DocKind.RECEIPT.path: [{"id": "1", "version": 3}, {"id": "2", "version": 7}]
        }
        adm = MockAdministration(documents)

        tag1, _changes1 = get_administration_changes(adm)
        _tag2, changes2 = get_administration_changes(adm, tag_bytes=tag1)

        self.assertDiffEqual(changes2[DocKind.RECEIPT], Diff())

    def test_remove(self):
        """
        Test requesting changes when documents are removed.

        If we request changes with a tag, and documents were removed on the remote,
        then those documents must be included in the diff as removed.
        """
        documents = {
            DocKind.PURCHASE_INVOICE.path: [
                {"id": "1", "version": 3},
                {"id": "2", "version": 7},
            ]
        }

        adm = MockAdministration(documents)

        tag1, _changes1 = get_administration_changes(adm)

        # remove documents
        ids_removed = [doc["id"] for doc in documents[DocKind.PURCHASE_INVOICE.path]]
        adm.documents.clear()

        _tag2, changes2 = get_administration_changes(adm, tag1)

        self.assertDiffEqual(
            changes2[DocKind.PURCHASE_INVOICE], Diff(removed=ids_removed)
        )

    def test_version_downgrade(self):
        """
        Test getting changes when a document version number is lowered.

        If the remote version has a document version which is lower than our current
        version for that document, then that document must be marked as 'changed' in
        the diff.
        """
        old_doc = {"id": "1", "version": 3}
        downgraded_doc = {"id": "1", "version": 2}

        documents = {DocKind.PURCHASE_INVOICE.path: [old_doc]}
        adm = MockAdministration(documents)

        tag1, _changes1 = get_administration_changes(adm)

        # downgrade document on the remote
        adm.documents[DocKind.PURCHASE_INVOICE.path][0] = downgraded_doc

        _tag2, changes2 = get_administration_changes(adm, tag1)

        self.assertDiffEqual(
            changes2[DocKind.PURCHASE_INVOICE], Diff(changed=[downgraded_doc])
        )

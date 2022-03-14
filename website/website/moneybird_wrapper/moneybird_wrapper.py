"""Moneybird API wrapper."""
from dataclasses import dataclass
from dataclasses import field
from typing import Iterable
from typing import Literal

from moneybird import MoneyBird as MoneyBirdApi
from moneybird import TokenAuthentication

DocId = str
DocVersion = int
DocKind = Literal["purchase_invoices", "receipts"]
DOCUMENT_KINDS: list[DocKind] = ["purchase_invoices", "receipts"]

Version = dict[DocId, DocVersion]
"""A function of document-id's to version numbers."""


@dataclass
class VersionDiff:
    """The difference between two versions."""

    added: list[DocId] = field(default_factory=list)
    changed: list[DocId] = field(default_factory=list)
    removed: list[DocId] = field(default_factory=list)


Document = dict


@dataclass
class Diff:
    """The difference between two lists of documents."""

    added: list[Document] = field(default_factory=list)
    changed: list[Document] = field(default_factory=list)
    removed: list[DocId] = field(default_factory=list)


@dataclass
class Tag:
    """A tag for a MoneyBird database state."""

    versions: dict[DocKind, Version] = field(default_factory=dict)


def diff_versions(old: Version, new: Version) -> VersionDiff:
    """Calculate the difference between two versions."""
    old_ids = old.keys()
    new_ids = new.keys()

    kept = old_ids & new_ids

    diff = VersionDiff()
    diff.added = list(new_ids - old_ids)
    diff.removed = list(old_ids - new_ids)
    diff.changed = list(filter(lambda doc_id: old[doc_id] < new[doc_id], kept))

    return diff


def chunk(lst: list, chunk_size: int) -> Iterable:
    """Split a list into chunks of size chunk_size."""
    for idx in range(0, len(lst), chunk_size):
        yield lst[idx : idx + 100]


class MoneyBirdApiWrapper:
    """A Moneybird API wrapper."""

    # pylint: disable=too-few-public-methods

    MAX_REQUEST_SIZE = 100

    def __init__(self, api):
        """
        Initialize the Moneybird Wrapper.

        :api: the underlying moneybird API
        """
        self.api = api
        self.administration_id = self.api.get("administrations")[0]["id"]

    def __get_remote_version(self, document_kind: DocKind) -> Version:
        documents = self.api.get(
            f"documents/{document_kind}/synchronization",
            administration_id=self.administration_id,
        )

        return {doc["id"]: doc["version"] for doc in documents}

    def __get_remote_documents_limited(
        self, kind: DocKind, ids: list[DocId]
    ) -> list[Document]:
        assert len(ids) <= self.MAX_REQUEST_SIZE

        return self.api.post(
            f"documents/{kind}/synchronization",
            data={"ids": ids},
            administration_id=self.administration_id,
        )

    def __get_remote_documents(self, kind: DocKind, ids: list[DocId]) -> list[Document]:
        """
        Load some documents of the specified kind.

        :param kind: the kind of document we want to load
        :param ids: the identifiers of the documents we want to load
        :return: the list of requested documents
        """
        if len(ids) == 0:
            return []

        documents = []

        for id_chunk in chunk(ids, self.MAX_REQUEST_SIZE):
            documents.extend(self.__get_remote_documents_limited(kind, id_chunk))

        return documents

    def get_changes(self, tag: Tag = None) -> tuple[Tag, dict[DocKind, Diff]]:
        """
        Get changes from MoneyBird.

        To get changes since a previous call, you can give the Tag returned by that previous call as a parameter.
        If no tag is given, all documents are returned.

        Returns a new Tag, and all changes that happened since the last get_changes call that returned the given Tag.

        """
        if tag is None:
            tag = Tag()

        new_tag = Tag()
        changes = {}

        for kind in DOCUMENT_KINDS:
            new_tag.versions[kind] = self.__get_remote_version(kind)

        for kind in DOCUMENT_KINDS:
            current = tag.versions[kind] if kind in tag.versions else {}
            remote = new_tag.versions[kind]
            version_diff = diff_versions(current, remote)

            diff = Diff()
            diff.added = self.__get_remote_documents(kind, version_diff.added)
            diff.changed = self.__get_remote_documents(kind, version_diff.changed)
            diff.removed = self.__get_remote_documents(kind, version_diff.removed)

            changes[kind] = diff

        return new_tag, changes


class MoneyBird(MoneyBirdApiWrapper):
    """A wrapper around the MoneyBird API."""

    # pylint: disable=too-few-public-methods

    def __init__(self, key: str):
        """
        Initialize the Moneybird Wrapper.

        :key: the API key
        """
        api = MoneyBirdApi(TokenAuthentication(key))
        super().__init__(api)

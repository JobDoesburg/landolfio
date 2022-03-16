"""Moneybird API wrapper."""
from dataclasses import dataclass
from dataclasses import field
from typing import Generator
from typing import Literal

from .api import Administration
from .api import HttpsAdministration

DocId = str
DocVersion = int
DocKind = Literal["purchase_invoices", "receipts"]
_DOCUMENT_KINDS: list[DocKind] = ["purchase_invoices", "receipts"]

Version = dict[DocId, DocVersion]
"""A function of document-ids to version numbers."""

_MAX_REQUEST_SIZE = 100


@dataclass
class VersionDiff:
    """The difference between two versions."""

    added: list[DocId] = field(default_factory=list)
    changed: list[DocId] = field(default_factory=list)
    removed: list[DocId] = field(default_factory=list)


Document = dict
"""A MoneyBird document."""


@dataclass
class Diff:
    """The difference between two sets of documents."""

    added: list[Document] = field(default_factory=list)
    changed: list[Document] = field(default_factory=list)
    removed: list[DocId] = field(default_factory=list)


Changes = dict[DocKind, Diff]
"""A dictionary with diffs per document kind."""


@dataclass
class Tag:
    """A tag for a MoneyBird database state."""

    versions: dict[DocKind, Version] = field(default_factory=dict)


def _diff_versions(old: Version, new: Version) -> VersionDiff:
    """Calculate the difference between two versions."""
    old_ids = old.keys()
    new_ids = new.keys()

    kept = old_ids & new_ids

    diff = VersionDiff()
    diff.added = list(new_ids - old_ids)
    diff.removed = list(old_ids - new_ids)
    diff.changed = list(filter(lambda doc_id: old[doc_id] < new[doc_id], kept))

    return diff


def _chunk(lst: list, chunk_size: int) -> Generator[list, None, None]:
    """Split a list into chunks of size chunk_size."""
    for idx in range(0, len(lst), chunk_size):
        yield lst[idx : idx + 100]


def _get_remote_version(api: Administration, document_kind: DocKind) -> Version:
    documents = api.get(
        f"documents/{document_kind}/synchronization",
    )

    return {doc["id"]: doc["version"] for doc in documents}


def _get_remote_documents_limited(
    api: Administration, kind: DocKind, ids: list[DocId]
) -> list[Document]:
    assert len(ids) <= _MAX_REQUEST_SIZE

    return api.post(
        f"documents/{kind}/synchronization",
        data={"ids": ids},
    )


def _get_remote_documents(
    api: Administration, kind: DocKind, ids: list[DocId]
) -> list[Document]:
    """
    Load some documents of the specified kind.

    :param kind: the kind of document we want to load
    :param ids: the identifiers of the documents we want to load
    :return: the list of requested documents
    """
    if len(ids) == 0:
        return []

    documents = []

    for id_chunk in _chunk(ids, _MAX_REQUEST_SIZE):
        documents.extend(_get_remote_documents_limited(api, kind, id_chunk))

    return documents


def _get_changes_from_api(api: Administration, tag: Tag = None) -> tuple[Tag, Changes]:
    if tag is None:
        tag = Tag()

    new_tag = Tag()
    changes = {}

    for kind in _DOCUMENT_KINDS:
        new_tag.versions[kind] = _get_remote_version(api, kind)

    for kind in _DOCUMENT_KINDS:
        current = tag.versions[kind] if kind in tag.versions else {}
        remote = new_tag.versions[kind]
        version_diff = _diff_versions(current, remote)

        diff = Diff()
        diff.added = _get_remote_documents(api, kind, version_diff.added)
        diff.changed = _get_remote_documents(api, kind, version_diff.changed)
        diff.removed = _get_remote_documents(api, kind, version_diff.removed)

        changes[kind] = diff

    return new_tag, changes


def get_changes(
    key: str, administration_id: int, tag: Tag = None
) -> tuple[Tag, Changes]:
    """
    Get changes from MoneyBird.

    To get changes since a previous call, you can give the Tag returned by that
    previous call as a parameter. If no tag is given, all documents are returned.

    Returns a new Tag, and all changes that happened since the last get_changes call
    that returned the given Tag.
    """
    api = HttpsAdministration(key, administration_id)
    return _get_changes_from_api(api, tag)

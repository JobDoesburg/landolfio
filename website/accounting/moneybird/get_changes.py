"""The module containing the 'get_administration_changes' function."""
import json
import typing
from dataclasses import dataclass
from dataclasses import field
from typing import Generator
from typing import Literal

from django.utils.translation import gettext as _

from .administration import Administration

DocId = str
DocVersion = int

DocKind = Literal["PI", "RC"]
DOCUMENT_KINDS: typing.Tuple[DocKind, ...] = typing.get_args(DocKind)


def path_for_kind(doc_kind: DocKind) -> str:
    """Get the moneybird administration resource path for a document kind."""
    if doc_kind == "PI":
        return "documents/purchase_invoices"
    if doc_kind == "RC":
        return "documents/receipts"

    if doc_kind in DOCUMENT_KINDS:
        raise NotImplementedError(
            f"Document kind '{doc_kind}' is not yet added to path_for_kind()."
        )

    raise ValueError(f"There is no such document kind: {doc_kind}.")


def name_for_kind(doc_kind: DocKind) -> str:
    """Get the human-readable name for a document kind."""
    if doc_kind == "PI":
        return _("Purchase Invoice")
    if doc_kind == "RC":
        return _("Receipt")

    if doc_kind in DOCUMENT_KINDS:
        raise NotImplementedError(
            f"Document kind '{doc_kind}' is not yet added to name_for_kind()."
        )

    raise ValueError(f"There is no such document kind: {doc_kind}.")


Version = dict[DocId, DocVersion]
"""A function of document-ids to version numbers."""

_MAX_REQUEST_SIZE = 100
"""The maximum number of documents that may be requested in one API-request."""


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

Tag = dict[DocKind, Version]
"""A tag for a MoneyBird database state."""


def _deserialize_tag(tag_bytes: bytes) -> Tag:
    return json.loads(tag_bytes.decode())


def _serialize_tag(tag: Tag) -> bytes:
    return json.dumps(tag).encode()


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
        yield lst[idx : idx + chunk_size]


def _get_remote_version(adm: Administration, doc_kind: DocKind) -> Version:
    documents = adm.get(
        f"{path_for_kind(doc_kind)}/synchronization",
    )

    return {doc["id"]: doc["version"] for doc in documents}


def _get_remote_documents_limited(
    adm: Administration, doc_kind: DocKind, ids: list[DocId]
) -> list[Document]:
    assert len(ids) <= _MAX_REQUEST_SIZE

    return adm.post(
        f"{path_for_kind(doc_kind)}/synchronization",
        data={"ids": ids},
    )


def _get_remote_documents(
    adm: Administration, kind: DocKind, ids: list[DocId]
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
        documents.extend(_get_remote_documents_limited(adm, kind, id_chunk))

    return documents


def _get_administration_changes_impl(
    adm: Administration, old_tag: Tag
) -> tuple[Tag, Changes]:
    changes = {}
    new_tag = Tag()

    for kind in DOCUMENT_KINDS:
        new_tag[kind] = _get_remote_version(adm, kind)

    for kind in DOCUMENT_KINDS:
        current = old_tag[kind] if kind in old_tag else {}
        remote = new_tag[kind]
        version_diff = _diff_versions(current, remote)

        diff = Diff()
        diff.added = _get_remote_documents(adm, kind, version_diff.added)
        diff.changed = _get_remote_documents(adm, kind, version_diff.changed)
        diff.removed = version_diff.removed

        changes[kind] = diff

    return new_tag, changes


def get_administration_changes(
    adm: Administration, tag_bytes: bytes = None
) -> tuple[bytes, Changes]:
    """
    Get changes from an administration.

    To get changes since a previous call, you can give the Tag returned by that
    previous call as a parameter. If no tag is given, all documents are returned.

    Returns a new Tag, and all changes that happened since the last get_changes call
    that returned the given Tag.
    """
    if tag_bytes is None:
        old_tag = Tag()
    else:
        old_tag = _deserialize_tag(tag_bytes)

    new_tag, changes = _get_administration_changes_impl(adm, old_tag)

    return _serialize_tag(new_tag), changes

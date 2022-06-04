"""The module containing the 'get_administration_changes' function."""
import copy
import json
from dataclasses import dataclass
from dataclasses import field
from enum import Enum
from typing import Generator

from django.utils.functional import classproperty
from django.utils.translation import gettext as _

from .administration import Administration

DocId = str
DocVersion = int


class DocKind(str, Enum):
    """A Moneybird administration document kind."""

    def __new__(cls, value, *_args):
        """Create and return a new DocKind object."""
        obj = str.__new__(cls, value)
        obj._value_ = value
        return obj

    def __init__(self, _value, human_readable_name, adm_path, user_path):
        """Initialize self."""
        self._human_readable_name = human_readable_name
        self._adm_path = adm_path
        self._user_path = user_path
        super().__init__()

    @property
    def human_readable_name(self):
        """Return the human readable name for this DocKind."""
        return self._human_readable_name

    @property
    def adm_path(self):
        """Return the administration path for this DocKind."""
        return self._adm_path

    @property
    def user_path(self):
        """
        Return the user path for this DocKind.

        This is used for building the web-URL of a document with this path.
        """
        return self._user_path

    PURCHASE_INVOICE = (
        "PI",
        _("Purchase Invoice"),
        "documents/purchase_invoices",
        "documents",
    )
    SALES_INVOICE = ("SI", _("Sales Invoice"), "sales_invoices", "sales_invoices")
    RECEIPT = ("RC", _("Receipt"), "documents/receipts", "documents")

    @classproperty
    def choices(cls):
        """Get the Django choices for document kinds."""
        # pylint: disable=no-self-argument
        return [(choice.value, choice.human_readable_name) for choice in cls]


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
    diff.changed = list(filter(lambda doc_id: old[doc_id] != new[doc_id], kept))

    return diff


def _chunk(lst: list, chunk_size: int) -> Generator[list, None, None]:
    """Split a list into chunks of size chunk_size."""
    for idx in range(0, len(lst), chunk_size):
        yield lst[idx : idx + chunk_size]


def _get_remote_version(adm: Administration, doc_kind: DocKind) -> Version:
    documents = adm.get(
        f"{doc_kind.adm_path}/synchronization",
    )

    return {doc["id"]: doc["version"] for doc in documents}


def _get_remote_documents_limited(
    adm: Administration, doc_kind: DocKind, ids: list[DocId]
) -> list[Document]:
    assert len(ids) <= _MAX_REQUEST_SIZE

    return adm.post(
        f"{doc_kind.adm_path}/synchronization",
        data={"ids": ids},
    )


def _get_remote_documents_greedy(
    adm: Administration, kind: DocKind, ids: list[DocId]
) -> list[Document]:
    """
    Load as many documents as possible of the specified kind.

    Try to retrieve requested documents, untill either all documents have been
    returned or the rate-limit was exceeded.

    :param kind: the kind of document we want to load
    :param ids: the identifiers of the documents we want to load
    :return: the list of requested documents
    """
    if len(ids) == 0:
        return []

    documents = []

    for id_chunk in _chunk(ids, _MAX_REQUEST_SIZE):
        try:
            documents.extend(_get_remote_documents_limited(adm, kind, id_chunk))
        except Administration.Throttled:
            break

    return documents


def _get_administration_changes_impl(
    adm: Administration, old_tag: Tag
) -> tuple[Tag, Changes]:
    changes = {}
    for kind in DocKind:
        if kind not in old_tag:
            old_tag[kind] = {}

    for kind in DocKind:
        try:
            remote = _get_remote_version(adm, kind)
        except Administration.Throttled:
            break

        current = old_tag[kind]
        version_diff = _diff_versions(current, remote)

        diff = Diff()
        diff.added = _get_remote_documents_greedy(adm, kind, version_diff.added)
        diff.changed = _get_remote_documents_greedy(adm, kind, version_diff.changed)
        diff.removed = version_diff.removed

        changes[kind] = diff

    new_tag = copy.deepcopy(old_tag)

    for kind, diff in changes.items():
        for doc_id in diff.removed:
            new_tag[kind].pop(doc_id)

        for doc in diff.added + diff.changed:
            doc_id = doc["id"]
            doc_version = doc["version"]
            new_tag[kind][doc_id] = doc_version

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

"""
Provides the sync_database function.

This module is responsible for getting changes from MoneyBird and applying those
changes in the database.
"""
from typing import Union

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.files.storage import Storage

from . import moneybird as mb
from .models import Document
from .models import DocumentLine


_TAG_PATH = "accounting/sync_database/tag"


def _load_tag_from_storage(storage: Storage) -> Union[bytes, None]:
    if not storage.exists(_TAG_PATH):
        return None

    return storage.open(_TAG_PATH).read()


def _save_tag_to_storage(tag: bytes, storage: Storage) -> None:
    assert isinstance(tag, bytes)

    if storage.exists(_TAG_PATH):
        storage.delete(_TAG_PATH)

    storage.save(_TAG_PATH, ContentFile(tag))


def _model_kind_from_moneybird_kind(kind: mb.DocKind) -> Document.Kind:
    if kind == "purchase_invoices":
        return Document.Kind.PURCHASE_INVOICE
    if kind == "receipts":
        return Document.Kind.RECEIPT

    raise NotImplementedError(f"Unhandled kind '{kind}'.")


def _add_docs_of_kind_to_db(kind: Document.Kind, docs: list[mb.Document]) -> None:
    for doc_data in docs:
        doc_id = int(doc_data["id"])
        doc = Document.objects.create(id_MB=doc_id, json_MB=doc_data, kind=kind)

        for line_data in doc_data["details"]:
            DocumentLine.objects.create(document=doc, json_MB=line_data)


def _change_docs_of_kind_in_db(kind: Document.Kind, docs: list[mb.Document]) -> None:
    for doc_data in docs:
        doc_id = int(doc_data["id"])

        # Change the document itself
        document = Document.objects.get(id_MB=doc_id, kind=kind)
        document.json_MB = doc_data
        document.save()

        # Remove all current document lines connected to this document
        document.documentline_set.all().delete()

        # Add all document lines
        for line_data in doc_data["details"]:
            DocumentLine.objects.create(document=document, json_MB=line_data)


def _remove_docs_of_kind_from_db(kind: Document.Kind, docs: list[mb.DocId]) -> None:
    for doc_id in docs:
        Document.objects.get(id_MB=doc_id, kind=kind).delete()


def _update_db_for_doc_kind(kind: Document.Kind, diff: mb.Diff) -> None:
    _add_docs_of_kind_to_db(kind, diff.added)
    _change_docs_of_kind_in_db(kind, diff.changed)
    _remove_docs_of_kind_from_db(kind, diff.removed)


def _sync_db_from_adm(adm: mb.Administration, storage: Storage) -> None:
    old_tag = _load_tag_from_storage(storage)
    new_tag, changes = mb.get_administration_changes(adm, old_tag)

    for doc_kind, changes_kind in changes.items():
        kind = _model_kind_from_moneybird_kind(doc_kind)
        _update_db_for_doc_kind(kind, changes_kind)

    _save_tag_to_storage(new_tag, storage)


def sync_database() -> None:
    """
    Synchronize the database to the remote MoneyBird administration.

    Get changes from the remote MoneyBird administration and apply them in the database.

    This function expects the following Django settings to be set:
     - MONEYBIRD_ADMINISTRATION_ID
     - MONEYBIRD_API_KEY
    """
    administration_id = settings.MONEYBIRD_ADMINISTRATION_ID
    key = settings.MONEYBIRD_API_KEY
    administration = mb.HttpsAdministration(key, administration_id)

    _sync_db_from_adm(administration, default_storage)

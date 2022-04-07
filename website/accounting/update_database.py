"""
Provides the update_database function.

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


_TAG_PATH = "accounting/update_database/tag"


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
    for doc in docs:
        doc_id = int(doc["id"])
        Document.objects.create(id_MB=doc_id, json_MB=doc, kind=kind)


def _change_docs_of_kind_in_db(kind: Document.Kind, docs: list[mb.Document]) -> None:
    for doc in docs:
        doc_id = int(doc["id"])
        document = Document.objects.get(id_MB=doc_id, kind=kind)
        document.json_MB = doc
        document.save()


def _remove_docs_of_kind_from_db(kind: Document.Kind, docs: list[mb.DocId]) -> None:
    for doc_id in docs:
        Document.objects.get(id_MB=doc_id, kind=kind).delete()


def _update_db_for_doc_kind(kind: Document.Kind, diff: mb.Diff) -> None:
    _add_docs_of_kind_to_db(kind, diff.added)
    _change_docs_of_kind_in_db(kind, diff.changed)
    _remove_docs_of_kind_from_db(kind, diff.removed)


def _update_db_from_api(api: mb.Administration, storage: Storage) -> None:
    old_tag = _load_tag_from_storage(storage)
    new_tag, changes = mb.get_changes_from_api(api, old_tag)

    for doc_kind, changes_kind in changes.items():
        kind = _model_kind_from_moneybird_kind(doc_kind)
        _update_db_for_doc_kind(kind, changes_kind)

    _save_tag_to_storage(new_tag, storage)


def update_database() -> None:
    """
    Update the database from the Remote MoneyBird.

    Get changes from the remote MoneyBird administration and apply them in the database.

    This function expects the following Django settings to be set:
     - MONEYBIRD_ADMINISTRATION_ID
     - MONEYBIRD_API_KEY
    """
    administration_id = settings.MONEYBIRD_ADMINISTRATION_ID
    key = settings.MONEYBIRD_API_KEY
    administration = mb.HttpsAdministration(key, administration_id)

    _update_db_from_api(administration, default_storage)

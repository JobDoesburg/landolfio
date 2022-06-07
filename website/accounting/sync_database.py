"""
Provides the sync_database function.

This module is responsible for getting changes from MoneyBird and applying those
changes in the database.
"""
import re
import threading
from typing import Union

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.files.storage import Storage
from inventory.models import Asset

from . import moneybird as mb
from .models import Document
from .models import DocumentLine
from .models import Ledger

_TAG_PATH = "accounting/sync_database/tag"

sync_lock = threading.Lock()


def _load_tag_from_storage(storage: Storage) -> Union[bytes, None]:
    if not storage.exists(_TAG_PATH):
        return None

    return storage.open(_TAG_PATH).read()


def _save_tag_to_storage(tag: bytes, storage: Storage) -> None:
    assert isinstance(tag, bytes)

    if storage.exists(_TAG_PATH):
        storage.delete(_TAG_PATH)

    storage.save(_TAG_PATH, ContentFile(tag))


def _find_asset_id_from_description(description: str) -> Union[str, None]:
    match = re.search(r"\[\s*([\w\d]+)\s*\]", description)

    if match is None:
        return None

    return match.group(1)


def _find_asset_from_id(asset_id) -> Union[Asset, None]:
    if asset_id is None:
        return None

    try:
        return Asset.objects.get(id=asset_id)
    except Asset.DoesNotExist:
        return None


def _add_doc_lines_to_db(doc: Document) -> None:
    assert doc.documentline_set.count() == 0
    for line_data in doc.moneybird_json["details"]:
        line_description = line_data["description"]
        asset_id = _find_asset_id_from_description(line_description)
        asset_or_none = _find_asset_from_id(asset_id)
        ledger_account_id = int(line_data["ledger_account_id"])

        price = line_data["total_price_excl_tax_with_discount_base"]
        ledger, _ledger_created = Ledger.objects.get_or_create(
            moneybird_id=ledger_account_id
        )

        DocumentLine.objects.create(
            document=doc,
            moneybird_json=line_data,
            asset=asset_or_none,
            asset_id_field=asset_id,
            ledger=ledger,
            price=price,
        )


def _add_docs_of_kind_to_db(kind: mb.DocKind, docs: list[mb.Document]) -> None:
    for doc_data in docs:
        doc_id = int(doc_data["id"])
        doc = Document.objects.create(
            moneybird_id=doc_id, moneybird_json=doc_data, kind=kind
        )
        _add_doc_lines_to_db(doc)


def _change_docs_of_kind_in_db(kind: mb.DocKind, docs: list[mb.Document]) -> None:
    for doc_data in docs:
        doc_id = int(doc_data["id"])

        # Change the document itself
        document = Document.objects.get(moneybird_id=doc_id, kind=kind)
        document.moneybird_json = doc_data
        document.save()

        # Remove all current document lines connected to this document
        document.documentline_set.all().delete()

        # Add all document lines
        _add_doc_lines_to_db(document)


def _remove_docs_of_kind_from_db(kind: mb.DocKind, docs: list[mb.DocId]) -> None:
    for doc_id in docs:
        Document.objects.get(moneybird_id=doc_id, kind=kind).delete()


def _update_db_for_doc_kind(kind: mb.DocKind, diff: mb.Diff) -> None:
    _add_docs_of_kind_to_db(kind, diff.added)
    _change_docs_of_kind_in_db(kind, diff.changed)
    _remove_docs_of_kind_from_db(kind, diff.removed)


def _sync_db_from_adm(adm: mb.Administration, storage: Storage) -> None:
    old_tag = _load_tag_from_storage(storage)
    new_tag, changes = mb.get_administration_changes(adm, old_tag)

    for kind, changes_kind in changes.items():
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
    # pylint: disable=consider-using-with
    locked = sync_lock.acquire(blocking=False)
    if locked:
        try:
            administration_id = settings.MONEYBIRD_ADMINISTRATION_ID
            key = settings.MONEYBIRD_API_KEY
            administration = mb.HttpsAdministration(key, administration_id)

            _sync_db_from_adm(administration, default_storage)
        finally:
            sync_lock.release()

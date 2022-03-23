from django.conf import settings

from . import moneybird as mb
from .models import Document


def _load_tag_from_storage() -> bytes | None:
    # pylint: disable=fixme
    # TODO
    return None


def _save_tag_to_storage(_tag: bytes) -> None:
    # pylint: disable=fixme
    # TODO
    pass


def model_kind_from_moneybird_kind(kind: mb.DocKind) -> Document.Kind:
    if kind == "purchase_invoices":
        return Document.Kind.PURCHASE_INVOICE
    if kind == "receipts":
        return Document.Kind.RECEIPT

    raise NotImplementedError(f"Unhandled kind '{kind}'.")


def _add_documents_of_kind_to_db(kind: Document.Kind, docs: list[mb.Document]) -> None:
    for doc in docs:
        # pylint: disable=no-member
        Document.objects.create(json_MB=doc, kind=kind)


def _change_documents_of_kind_in_db(
    _kind: Document.Kind, _docs: list[mb.Document]
) -> None:
    # pylint: disable=fixme
    # TODO
    pass


def _remove_documents_of_kind_from_db(
    _kind: Document.Kind, _docs: list[mb.DocId]
) -> None:
    # pylint: disable=fixme
    # TODO
    pass


def _update_db_for_doc_kind(kind: Document.Kind, diff: mb.Diff) -> None:
    _add_documents_of_kind_to_db(kind, diff.added)
    _change_documents_of_kind_in_db(kind, diff.changed)
    _remove_documents_of_kind_from_db(kind, diff.removed)


def _update_db_from_api(api: mb.Administration) -> None:
    # pylint: disable=assignment-from-none
    old_tag = _load_tag_from_storage()
    new_tag, changes = mb.get_changes_from_api(api, old_tag)

    for doc_kind, changes_kind in changes.items():
        kind = model_kind_from_moneybird_kind(doc_kind)
        _update_db_for_doc_kind(kind, changes_kind)

    _save_tag_to_storage(new_tag)


def update_database() -> None:
    administration_id = settings.MONEYBIRD_ADMINISTRATION_ID
    key = settings.MONEYBIRD_API_KEY
    administration = mb.HttpsAdministration(key, administration_id)

    _update_db_from_api(administration)

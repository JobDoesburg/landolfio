from dataclasses import dataclass, field
from decimal import Decimal

from django.utils.translation import gettext as _

from accounting.models import (
    Contact,
    DocumentKind,
    JournalDocument,
    Subscription,
    Product,
    Ledger,
    LedgerKind,
    DocumentLine,
)

MoneybirdResourceId = str
MoneybirdResourceVersion = int
MoneybirdResource = dict


@dataclass
class ResourceDiff:
    added: list[MoneybirdResource] = field(default_factory=list)
    changed: list[MoneybirdResource] = field(default_factory=list)
    removed: list[MoneybirdResourceId] = field(default_factory=list)


@dataclass
class ResourceVersionDiff:
    added: list[MoneybirdResourceId] = field(default_factory=list)
    changed: list[MoneybirdResourceId] = field(default_factory=list)
    removed: list[MoneybirdResourceId] = field(default_factory=list)


class MoneybirdResourceType:
    human_readable_name = None
    api_path = None
    synchronizable = None
    model = None

    @classmethod
    def get_queryset(cls):
        return cls.model._default_manager.all()

    @classmethod
    def get_local_versions(cls) -> list[MoneybirdResourceId]:
        return list(
            map(
                MoneybirdResourceId,
                cls.get_queryset().values_list("moneybird_id", flat=True),
            )
        )

    @classmethod
    def get_model_kwargs(cls, data):
        return {"moneybird_id": MoneybirdResourceId(data["id"])}

    @classmethod
    def create_from_moneybird(cls, data: MoneybirdResource):
        return cls.model._default_manager.create(**cls.get_model_kwargs(data))

    @classmethod
    def update_from_moneybird(cls, data: MoneybirdResource):
        return cls.get_queryset().update_or_create(
            moneybird_id=MoneybirdResourceId(data["id"]),
            defaults={**cls.get_model_kwargs(data)},
        )

    @classmethod
    def delete_from_moneybird(cls, resource_id: MoneybirdResourceId):
        return cls.get_queryset().get(moneybird_id=resource_id).delete()

    @classmethod
    def update_resources(cls, diff: ResourceDiff):
        for resource in diff.added:
            cls.create_from_moneybird(resource)
        for resource in diff.changed:
            cls.update_from_moneybird(resource)
        for resource_id in diff.removed:
            cls.delete_from_moneybird(resource_id)

    @staticmethod
    def diff_resources(
        old: list[MoneybirdResourceId], new: list[MoneybirdResource]
    ) -> ResourceDiff:
        resources_diff = ResourceDiff()
        resources_diff.added = list(
            filter(lambda resource: resource["id"] not in old, new)
        )
        resources_diff.changed = list(
            filter(lambda resource: resource["id"] in old, new)
        )  # We can only consider every resource has changed if it is in the new list
        resources_diff.removed = list(
            filter(
                lambda resource: resource not in list(r["id"] for r in new),
                old,
            )
        )
        return resources_diff


class SynchronizableMoneybirdResourceType(MoneybirdResourceType):
    @classmethod
    def get_model_kwargs(cls, data):
        kwargs = super().get_model_kwargs(data)
        kwargs["version"] = MoneybirdResourceVersion(data["version"])
        return kwargs

    @classmethod
    def get_local_versions(cls) -> dict[MoneybirdResourceId, MoneybirdResourceVersion]:
        return dict(
            map(
                lambda x: (
                    MoneybirdResourceId(x[0]),
                    MoneybirdResourceVersion(x[1]),
                ),
                cls.get_queryset().values_list("moneybird_id", "version"),
            )
        )

    @staticmethod
    def diff_resource_versions(
        old: dict[MoneybirdResourceId, MoneybirdResourceVersion],
        new: dict[MoneybirdResourceId, MoneybirdResourceVersion],
    ) -> ResourceVersionDiff:
        old_ids = old.keys()
        new_ids = new.keys()

        kept = old_ids & new_ids

        diff = ResourceVersionDiff()
        diff.added = list(new_ids - old_ids)
        diff.removed = list(old_ids - new_ids)
        diff.changed = list(
            filter(lambda doc_id: old[doc_id] != new[doc_id], kept)
        )  # Check if the version has changed

        return diff


class MoneybirdResourceTypeWithDocumentLines(SynchronizableMoneybirdResourceType):
    @classmethod
    def get_local_document_line_versions(
        cls, document: JournalDocument
    ) -> list[MoneybirdResourceId]:
        return list(
            map(
                MoneybirdResourceId,
                cls.get_document_lines_queryset(document).values_list(
                    "moneybird_id", flat=True
                ),
            )
        )

    @classmethod
    def get_document_lines_queryset(cls, document: JournalDocument):
        return (
            document.document_lines.all()
        )  # TODO: Make document_lines a property of the model

    @classmethod
    def get_document_line_model_kwargs(cls, line_data: MoneybirdResource):
        return {"moneybird_id": MoneybirdResourceId(line_data["id"])}

    @classmethod
    def create_document_line_from_moneybird(
        cls, document: JournalDocument, line_data: MoneybirdResource
    ):
        return cls.get_document_lines_queryset(document).create(
            document=document, **cls.get_document_line_model_kwargs(line_data)
        )

    @classmethod
    def update_document_line_from_moneybird(
        cls, document: JournalDocument, line_data: MoneybirdResource
    ):
        return cls.get_document_lines_queryset(document).update_or_create(
            moneybird_id=MoneybirdResourceId(line_data["id"]),
            document=document,
            defaults={**cls.get_document_line_model_kwargs(line_data)},
        )

    @classmethod
    def delete_document_line_from_moneybird(
        cls, document: JournalDocument, resource_id: MoneybirdResourceId
    ):
        return (
            cls.get_document_lines_queryset(document)
            .get(moneybird_id=resource_id)
            .delete()
        )

    @classmethod
    def update_document_lines(
        cls, document: JournalDocument, document_lines_diff: ResourceDiff
    ):
        for document_line in document_lines_diff.added:
            cls.create_document_line_from_moneybird(document, document_line)
        for document_line in document_lines_diff.changed:
            cls.update_document_line_from_moneybird(document, document_line)
        for document_line_id in document_lines_diff.removed:
            cls.delete_document_line_from_moneybird(document, document_line_id)

    @classmethod
    def get_document_line_resource_data(
        cls, data: MoneybirdResource
    ) -> list[MoneybirdResource]:
        return data["details"]

    @classmethod
    def create_from_moneybird(cls, data: MoneybirdResource):
        document = super().create_from_moneybird(data)
        document_lines = cls.get_document_line_resource_data(data)
        for line_data in document_lines:
            cls.create_document_line_from_moneybird(document, line_data)

    @classmethod
    def update_from_moneybird(cls, data: MoneybirdResource):
        document, _ = super().update_from_moneybird(data)
        new_lines = cls.get_document_line_resource_data(data)
        old_lines = cls.get_local_document_line_versions(document)
        document_lines_diff = cls.diff_resources(old_lines, new_lines)
        cls.update_document_lines(document, document_lines_diff)


class JournalDocumentResourceType(MoneybirdResourceTypeWithDocumentLines):
    model = JournalDocument

    @classmethod
    def get_model_kwargs(cls, data):
        kwargs = super().get_model_kwargs(data)
        kwargs["moneybird_json"] = data
        return kwargs

    @classmethod
    def get_document_line_model_kwargs(cls, line_data: MoneybirdResource):
        kwargs = super().get_document_line_model_kwargs(line_data)
        kwargs["moneybird_json"] = line_data
        ledger_account_id = int(line_data["ledger_account_id"])
        ledger, _ = Ledger.objects.get_or_create(moneybird_id=ledger_account_id)
        kwargs["ledger"] = ledger
        return kwargs


class SalesInvoiceResourceType(JournalDocumentResourceType):
    human_readable_name = _("Sales invoice")
    api_path = "sales_invoices"

    @classmethod
    def get_queryset(cls):
        return super().get_queryset().filter(document_kind=DocumentKind.SALES_INVOICE)

    @classmethod
    def get_model_kwargs(cls, data):
        kwargs = super().get_model_kwargs(data)
        kwargs["document_kind"] = DocumentKind.SALES_INVOICE
        kwargs["date"] = data["invoice_date"]
        return kwargs

    @classmethod
    def get_document_line_model_kwargs(cls, line_data: MoneybirdResource):
        kwargs = super().get_document_line_model_kwargs(line_data)
        ledger = kwargs["ledger"]
        kwargs["price"] = line_data["total_price_excl_tax_with_discount_base"]
        if ledger.ledger_kind and ledger.ledger_kind in [
            LedgerKind.VOORRAAD_MARGE,
            LedgerKind.VOORRAAD_NIET_MARGE,
        ]:
            # TODO if ledger.kind is None, not doing this this will result in invalid data
            kwargs["price"] = -1 * Decimal(kwargs["price"])
        return kwargs


class PurchaseInvoiceDocumentResourceType(JournalDocumentResourceType):
    human_readable_name = _("Purchase invoice")
    api_path = "documents/purchase_invoices"

    @classmethod
    def get_queryset(cls):
        return (
            super().get_queryset().filter(document_kind=DocumentKind.PURCHASE_INVOICE)
        )

    @classmethod
    def get_model_kwargs(cls, data):
        kwargs = super().get_model_kwargs(data)
        kwargs["document_kind"] = DocumentKind.PURCHASE_INVOICE
        kwargs["date"] = data["date"]
        return kwargs

    @classmethod
    def get_document_line_model_kwargs(cls, line_data: MoneybirdResource):
        kwargs = super().get_document_line_model_kwargs(line_data)
        kwargs["price"] = line_data["total_price_excl_tax_with_discount_base"]
        return kwargs


class ReceiptResourceType(JournalDocumentResourceType):
    human_readable_name = _("Receipt")
    api_path = "documents/receipts"

    @classmethod
    def get_queryset(cls):
        return super().get_queryset().filter(document_kind=DocumentKind.RECEIPT)

    @classmethod
    def get_model_kwargs(cls, data):
        kwargs = super().get_model_kwargs(data)
        kwargs["document_kind"] = DocumentKind.RECEIPT
        kwargs["date"] = data["date"]
        return kwargs

    @classmethod
    def get_document_line_model_kwargs(cls, line_data: MoneybirdResource):
        kwargs = super().get_document_line_model_kwargs(line_data)
        kwargs["price"] = line_data["total_price_excl_tax_with_discount_base"]
        return kwargs


class GeneralJournalDocumentResourceType(JournalDocumentResourceType):
    human_readable_name = _("General journal document")
    api_path = "documents/general_journal_documents"

    @classmethod
    def get_queryset(cls):
        return (
            super()
            .get_queryset()
            .filter(document_kind=DocumentKind.GENERAL_JOURNAL_DOCUMENT)
        )

    @classmethod
    def get_model_kwargs(cls, data):
        kwargs = super().get_model_kwargs(data)
        kwargs["document_kind"] = DocumentKind.GENERAL_JOURNAL_DOCUMENT
        kwargs["date"] = data["date"]
        return kwargs

    @classmethod
    def get_document_line_resource_data(cls, data: MoneybirdResource):
        return data["general_journal_document_entries"]

    @classmethod
    def get_document_line_model_kwargs(cls, line_data: MoneybirdResource):
        kwargs = super().get_document_line_model_kwargs(line_data)
        kwargs["price"] = Decimal(line_data["debit"]) - Decimal(line_data["credit"])
        return kwargs


class ContactResourceType(SynchronizableMoneybirdResourceType):
    human_readable_name = _("Contact")
    api_path = "contacts"
    model = Contact

    @classmethod
    def get_model_kwargs(cls, data):
        kwargs = super().get_model_kwargs(data)
        kwargs["moneybird_json"] = data
        return kwargs


class ProductResourceType(MoneybirdResourceType):
    human_readable_name = _("Product")
    api_path = "products"
    model = Product

    @classmethod
    def get_model_kwargs(cls, data):
        kwargs = super().get_model_kwargs(data)
        kwargs["moneybird_json"] = data
        return kwargs


class LedgerAccountResourceType(MoneybirdResourceType):
    human_readable_name = _("Ledger account")
    api_path = "ledger_accounts"
    model = Ledger

    @classmethod
    def get_model_kwargs(cls, data):
        kwargs = super().get_model_kwargs(data)
        kwargs["name"] = data["name"]
        return kwargs


# class SubscriptionResourceType(MoneybirdResourceType):
#     human_readable_name = _("Subscription")
#     api_path = "subscriptions"
#     synchronizable = False
#     model = Subscription
#
#     @classmethod
#     def get_model_kwargs(cls, data):
#         kwargs = super().get_model_kwargs(data)
#         kwargs["moneybird_json"] = data
#         return kwargs
# TODO this can only be queried with contact id


MoneybirdResourceTypes = [
    SalesInvoiceResourceType,
    PurchaseInvoiceDocumentResourceType,
    ReceiptResourceType,
    GeneralJournalDocumentResourceType,
    GeneralJournalDocumentResourceType,
    ContactResourceType,
    LedgerAccountResourceType,
    ProductResourceType,
]

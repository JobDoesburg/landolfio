from decimal import Decimal

from django.db.models.functions import datetime

from accounting.models import (
    Contact,
    DocumentKind,
    JournalDocument,
    Subscription,
    Product,
    Ledger,
    LedgerKind,
    Estimate,
    RecurringSalesInvoice,
    Workflow,
    LedgerAccountType,
    JournalDocumentLine,
    EstimateDocumentLine,
    RecurringSalesInvoiceDocumentLine,
)

from moneybird.resource_types import (
    MoneybirdResourceId,
    MoneybirdResource,
    MoneybirdResourceType,
    SynchronizableMoneybirdResourceType,
    MoneybirdResourceTypeWithDocumentLines,
)


class JournalDocumentResourceType(MoneybirdResourceTypeWithDocumentLines):
    model = JournalDocument
    document_lines_model = JournalDocumentLine
    document_lines_foreign_key = "document_lines"
    document_foreign_key = "document"

    @classmethod
    def get_model_kwargs(cls, data):
        kwargs = super().get_model_kwargs(data)
        kwargs["moneybird_json"] = data
        return kwargs

    @classmethod
    def get_document_line_model_kwargs(cls, line_data: MoneybirdResource, document):
        kwargs = super().get_document_line_model_kwargs(line_data, document)
        kwargs["document"] = document
        kwargs["moneybird_json"] = line_data
        ledger_account_id = MoneybirdResourceId(line_data["ledger_account_id"])
        ledger, _ = Ledger.objects.get_or_create(moneybird_id=ledger_account_id)
        kwargs["ledger"] = ledger
        return kwargs


class SalesInvoiceResourceType(JournalDocumentResourceType):
    entity_type = "SalesInvoice"
    entity_type_name = "sales_invoice"
    api_path = "sales_invoices"

    @classmethod
    def get_queryset(cls):
        return super().get_queryset().filter(document_kind=DocumentKind.SALES_INVOICE)

    @classmethod
    def get_model_kwargs(cls, data):
        kwargs = super().get_model_kwargs(data)
        kwargs["document_kind"] = DocumentKind.SALES_INVOICE
        kwargs["date"] = datetime.datetime.fromisoformat(data["invoice_date"]).date()
        if data["contact"]:
            contact_id = MoneybirdResourceId(data["contact"]["id"])
            contact, _ = Contact.objects.get_or_create(moneybird_id=contact_id)
            kwargs["contact"] = contact

        workflow_id = MoneybirdResourceId(data["workflow_id"])
        workflow, _ = Workflow.objects.get_or_create(moneybird_id=workflow_id)
        kwargs["workflow"] = workflow
        kwargs["total_price"] = data["total_price_incl_tax_base"]
        kwargs["total_paid"] = data["total_paid"]
        kwargs["total_unpaid"] = data["total_unpaid"]
        return kwargs

    @classmethod
    def serialize_for_moneybird(cls, instance):
        data = super().serialize_for_moneybird(instance)
        data["invoice_date"] = instance.date.isoformat()
        data["contact"] = instance.contact.moneybird_id if instance.contact else None
        data["workflow_id"] = (
            instance.workflow.moneybird_id if instance.workflow else None
        )
        return data

    @classmethod
    def serialize_document_line_for_moneybird(cls, document_line, document):
        data = super().serialize_document_line_for_moneybird(document_line, document)
        data["description"] = "test"  # TODO fix this
        data["price"] = float(document_line.price)
        if document_line.ledger:
            data["ledger_account_id"] = MoneybirdResourceId(
                document_line.ledger.moneybird_id
            )
            if (
                document_line.ledger.account_type
                and document_line.ledger.account_type
                == LedgerAccountType.NON_CURRENT_ASSETS
            ):
                data["price"] = float(-1 * document_line.price)  # TODO is dit handig?
        return data

    @classmethod
    def get_document_line_model_kwargs(cls, line_data: MoneybirdResource, document):
        kwargs = super().get_document_line_model_kwargs(line_data, document)
        ledger = kwargs["ledger"]
        kwargs["price"] = line_data["total_price_excl_tax_with_discount_base"]
        if (
            ledger.account_type
            and ledger.account_type == LedgerAccountType.NON_CURRENT_ASSETS
        ):
            kwargs["price"] = -1 * Decimal(kwargs["price"])  # TODO is dit handig?
        return kwargs


class PurchaseInvoiceDocumentResourceType(JournalDocumentResourceType):
    entity_type = "PurchaseInvoice"
    entity_type_name = "purchase_invoice"
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
        kwargs["date"] = datetime.datetime.fromisoformat(data["date"]).date()
        if data["contact"]:
            contact_id = MoneybirdResourceId(data["contact"]["id"])
            contact, _ = Contact.objects.get_or_create(moneybird_id=contact_id)
            kwargs["contact"] = contact
        kwargs["total_price"] = data["total_price_incl_tax_base"]
        return kwargs

    @classmethod
    def get_document_line_model_kwargs(cls, line_data: MoneybirdResource, document):
        kwargs = super().get_document_line_model_kwargs(line_data, document)
        kwargs["price"] = line_data["total_price_excl_tax_with_discount_base"]
        return kwargs


class ReceiptResourceType(JournalDocumentResourceType):
    entity_type = "Receipt"
    entity_type_name = "receipt"
    api_path = "documents/receipts"

    @classmethod
    def get_queryset(cls):
        return super().get_queryset().filter(document_kind=DocumentKind.RECEIPT)

    @classmethod
    def get_model_kwargs(cls, data):
        kwargs = super().get_model_kwargs(data)
        kwargs["document_kind"] = DocumentKind.RECEIPT
        kwargs["date"] = datetime.datetime.fromisoformat(data["date"]).date()
        if data["contact"]:
            contact_id = MoneybirdResourceId(data["contact"]["id"])
            contact, _ = Contact.objects.get_or_create(moneybird_id=contact_id)
            kwargs["contact"] = contact
        kwargs["total_price"] = data["total_price_incl_tax_base"]
        return kwargs

    @classmethod
    def get_document_line_model_kwargs(cls, line_data: MoneybirdResource, document):
        kwargs = super().get_document_line_model_kwargs(line_data, document)
        kwargs["price"] = line_data["total_price_excl_tax_with_discount_base"]
        return kwargs


class GeneralJournalDocumentResourceType(JournalDocumentResourceType):
    entity_type = "GeneralJournalDocument"
    entity_type_name = "general_journal_document"
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
        kwargs["date"] = datetime.datetime.fromisoformat(data["date"]).date()
        return kwargs

    @classmethod
    def get_document_line_resource_data(cls, data: MoneybirdResource):
        return data["general_journal_document_entries"]

    @classmethod
    def get_document_line_model_kwargs(cls, line_data: MoneybirdResource, document):
        kwargs = super().get_document_line_model_kwargs(line_data, document)
        kwargs["price"] = Decimal(line_data["debit"]) - Decimal(line_data["credit"])
        return kwargs


class ContactResourceType(SynchronizableMoneybirdResourceType):
    entity_type = "Contact"
    entity_type_name = "contact"
    api_path = "contacts"
    model = Contact

    @classmethod
    def get_model_kwargs(cls, data):
        kwargs = super().get_model_kwargs(data)
        kwargs["moneybird_json"] = data
        kwargs["company_name"] = data["company_name"]
        kwargs["first_name"] = data["firstname"]
        kwargs["last_name"] = data["lastname"]
        kwargs["email"] = data["email"]
        kwargs["sepa_active"] = data["sepa_active"]
        return kwargs

    @classmethod
    def serialize_for_moneybird(cls, instance):
        return {
            "company_name": instance.company_name,
            "firstname": instance.first_name,
            "lastname": instance.last_name,
            "send_invoices_to_email": instance.email,
            "send_estimates_to_email": instance.email,
        }


class ProductResourceType(MoneybirdResourceType):
    api_path = "products"
    entity_type_name = "product"
    model = Product

    @classmethod
    def get_model_kwargs(cls, data):
        kwargs = super().get_model_kwargs(data)
        kwargs["moneybird_json"] = data
        return kwargs


class LedgerAccountResourceType(MoneybirdResourceType):
    entity_type = "LedgerAccount"
    api_path = "ledger_accounts"
    entity_type_name = "ledger_account"
    model = Ledger

    @classmethod
    def get_model_kwargs(cls, data):
        kwargs = super().get_model_kwargs(data)
        kwargs["name"] = data["name"]
        kwargs["account_type"] = data["account_type"]
        return kwargs


class EstimateResourceType(MoneybirdResourceTypeWithDocumentLines):
    entity_type = "Estimate"
    entity_type_name = "estimate"
    api_path = "estimates"
    model = Estimate
    document_lines_model = EstimateDocumentLine
    document_lines_foreign_key = "document_lines"
    document_foreign_key = "document"

    @classmethod
    def get_model_kwargs(cls, data):
        kwargs = super().get_model_kwargs(data)
        kwargs["moneybird_json"] = data
        if data["contact"]:
            contact_id = MoneybirdResourceId(data["contact"]["id"])
            contact, _ = Contact.objects.get_or_create(moneybird_id=contact_id)
            kwargs["contact"] = contact

        workflow_id = MoneybirdResourceId(data["workflow_id"])
        workflow, _ = Workflow.objects.get_or_create(moneybird_id=workflow_id)
        kwargs["workflow"] = workflow
        kwargs["total_price"] = data["total_price_incl_tax_base"]

        return kwargs

    @classmethod
    def get_document_line_model_kwargs(cls, line_data: MoneybirdResource, document):
        kwargs = super().get_document_line_model_kwargs(line_data, document)
        kwargs["document"] = document
        kwargs["moneybird_json"] = line_data
        return kwargs


class RecurringSalesInvoiceResourceType(MoneybirdResourceTypeWithDocumentLines):
    entity_type = "RecurringSalesInvoice"
    entity_type_name = "recurring_sales_invoice"
    api_path = "recurring_sales_invoices"
    model = RecurringSalesInvoice
    document_lines_model = RecurringSalesInvoiceDocumentLine
    document_lines_foreign_key = "document_lines"
    document_foreign_key = "document"

    @classmethod
    def get_model_kwargs(cls, data):
        kwargs = super().get_model_kwargs(data)
        kwargs["moneybird_json"] = data
        kwargs["auto_send"] = data["auto_send"]
        kwargs["active"] = data["active"]
        kwargs["frequency"] = data["frequency_type"]
        kwargs["start_date"] = data["start_date"]
        kwargs["invoice_date"] = data["invoice_date"]
        kwargs["last_date"] = data["last_date"]
        kwargs["moneybird_json"] = data
        if data["contact"]:
            contact_id = MoneybirdResourceId(data["contact"]["id"])
            contact, _ = Contact.objects.get_or_create(moneybird_id=contact_id)
            kwargs["contact"] = contact

        workflow_id = MoneybirdResourceId(data["workflow_id"])
        workflow, _ = Workflow.objects.get_or_create(moneybird_id=workflow_id)
        kwargs["workflow"] = workflow
        kwargs["total_price"] = data["total_price_incl_tax_base"]

        return kwargs

    @classmethod
    def get_document_line_model_kwargs(cls, line_data: MoneybirdResource, document):
        kwargs = super().get_document_line_model_kwargs(line_data, document)
        kwargs["document"] = document
        kwargs["moneybird_json"] = line_data
        return kwargs


class WorkflowResourceType(MoneybirdResourceType):
    entity_type = "Workflow"
    entity_type_name = "workflow"
    api_path = "workflows"
    model = Workflow
    can_write = False

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
#     def get_model_kwargs(cls, resource_data):
#         kwargs = super().get_model_kwargs(resource_data)
#         kwargs["moneybird_json"] = resource_data
#         return kwargs
# TODO this can only be queried with contact id

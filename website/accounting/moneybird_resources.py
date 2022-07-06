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
    Estimate,
    RecurringSalesInvoice,
    Workflow,
    LedgerAccountType,
)

from accounting.moneybird.resource_types import (
    MoneybirdResourceId,
    MoneybirdResource,
    MoneybirdResourceType,
    SynchronizableMoneybirdResourceType,
    MoneybirdResourceTypeWithDocumentLines,
)


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
        ledger_account_id = MoneybirdResourceId(line_data["ledger_account_id"])
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
    def get_document_line_model_kwargs(cls, line_data: MoneybirdResource):
        kwargs = super().get_document_line_model_kwargs(line_data)
        ledger = kwargs["ledger"]
        kwargs["price"] = line_data["total_price_excl_tax_with_discount_base"]
        if (
            ledger.account_type
            and ledger.account_type == LedgerAccountType.NON_CURRENT_ASSETS
        ):
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
        if data["contact"]:
            contact_id = MoneybirdResourceId(data["contact"]["id"])
            contact, _ = Contact.objects.get_or_create(moneybird_id=contact_id)
            kwargs["contact"] = contact
        kwargs["total_price"] = data["total_price_incl_tax_base"]
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
        if data["contact"]:
            contact_id = MoneybirdResourceId(data["contact"]["id"])
            contact, _ = Contact.objects.get_or_create(moneybird_id=contact_id)
            kwargs["contact"] = contact
        kwargs["total_price"] = data["total_price_incl_tax_base"]
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
        kwargs["company_name"] = data["company_name"]
        kwargs["first_name"] = data["firstname"]
        kwargs["last_name"] = data["lastname"]
        kwargs["email"] = data["email"]
        kwargs["sepa_active"] = data["sepa_active"]
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
        kwargs["account_type"] = data["account_type"]
        return kwargs


class EstimateResourceType(MoneybirdResourceTypeWithDocumentLines):
    human_readable_name = _("Estimate")
    api_path = "estimates"
    model = Estimate

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
    def get_document_line_model_kwargs(cls, line_data: MoneybirdResource):
        kwargs = super().get_document_line_model_kwargs(line_data)
        kwargs["moneybird_json"] = line_data
        return kwargs


class RecurringSalesInvoiceResourceType(MoneybirdResourceTypeWithDocumentLines):
    human_readable_name = _("Recurring sales invoice")
    api_path = "recurring_sales_invoices"
    model = RecurringSalesInvoice

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
    def get_document_line_model_kwargs(cls, line_data: MoneybirdResource):
        kwargs = super().get_document_line_model_kwargs(line_data)
        kwargs["moneybird_json"] = line_data
        return kwargs


class WorkflowResourceType(MoneybirdResourceType):
    human_readable_name = _("Workflow")
    api_path = "workflows"
    model = Workflow

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

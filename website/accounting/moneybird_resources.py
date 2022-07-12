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
    Project,
    TaxRate,
)

from moneybird.resource_types import (
    MoneybirdResourceId,
    MoneybirdResource,
    MoneybirdResourceTypeWithDocumentLines,
)
from moneybird import resources


def _get_workflow_from_moneybird_data(data: MoneybirdResource):
    if not data["workflow_id"]:
        return None
    workflow_id = MoneybirdResourceId(data["workflow_id"])
    workflow, _ = Workflow.objects.get_or_create(moneybird_id=workflow_id)
    return workflow


def _get_ledger_from_moneybird_data(data: MoneybirdResource):
    if not data["ledger_account_id"]:
        return None
    ledger_account_id = MoneybirdResourceId(data["ledger_account_id"])
    ledger, _ = Ledger.objects.get_or_create(moneybird_id=ledger_account_id)
    return ledger


def _get_project_from_moneybird_data(data: MoneybirdResource):
    if not data["project_id"]:
        return None
    project_id = MoneybirdResourceId(data["project_id"])
    project, _ = Project.objects.get_or_create(moneybird_id=project_id)
    return project


def _get_contact_from_moneybird_data(data: MoneybirdResource):
    if not data["contact"]:
        return None
    contact_id = MoneybirdResourceId(data["contact"]["id"])
    contact, _ = Contact.objects.get_or_create(moneybird_id=contact_id)
    return contact


def _get_tax_rate_from_moneybird_data(data: MoneybirdResource):
    if not data["tax_rate_id"]:
        return None
    tax_rate_id = MoneybirdResourceId(data["tax_rate_id"])
    tax_rate, _ = TaxRate.objects.get_or_create(moneybird_id=tax_rate_id)
    return tax_rate


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
        kwargs["description"] = line_data["description"]
        kwargs["ledger"] = _get_ledger_from_moneybird_data(line_data)
        kwargs["project"] = _get_project_from_moneybird_data(line_data)
        kwargs["moneybird_json"] = line_data
        return kwargs


class SalesInvoiceResourceType(
    resources.SalesInvoiceResourceType, JournalDocumentResourceType
):
    @classmethod
    def get_queryset(cls):
        return super().get_queryset().filter(document_kind=DocumentKind.SALES_INVOICE)

    @classmethod
    def get_model_kwargs(cls, data):
        kwargs = super().get_model_kwargs(data)
        kwargs["document_kind"] = DocumentKind.SALES_INVOICE
        kwargs["date"] = datetime.datetime.fromisoformat(data["invoice_date"]).date()
        kwargs["contact"] = _get_contact_from_moneybird_data(data)
        kwargs["workflow"] = _get_workflow_from_moneybird_data(data)
        kwargs["total_price"] = data["total_price_incl_tax_base"]
        kwargs["total_paid"] = data["total_paid"]
        kwargs["total_unpaid"] = data["total_unpaid"]
        return kwargs

    @classmethod
    def get_document_line_model_kwargs(cls, line_data: MoneybirdResource, document):
        kwargs = super().get_document_line_model_kwargs(line_data, document)
        kwargs["amount"] = line_data["amount"]
        kwargs["tax_rate"] = _get_tax_rate_from_moneybird_data(line_data)
        ledger = kwargs["ledger"]
        kwargs["price"] = line_data["total_price_excl_tax_with_discount_base"]
        if (
            ledger.account_type
            and ledger.account_type == LedgerAccountType.NON_CURRENT_ASSETS
        ):
            kwargs["price"] = -1 * Decimal(kwargs["price"])  # TODO is dit handig?
        return kwargs

    @classmethod
    def serialize_for_moneybird(cls, instance):
        data = super().serialize_for_moneybird(instance)
        data["invoice_date"] = instance.date.isoformat()
        if instance.contact:
            data["contact"] = MoneybirdResourceId(instance.contact.moneybird_id)
        if instance.workflow:
            data["workflow_id"] = MoneybirdResourceId(instance.workflow.moneybird_id)
        return data

    @classmethod
    def serialize_document_line_for_moneybird(cls, document_line, document):
        data = super().serialize_document_line_for_moneybird(document_line, document)
        data["description"] = document_line.description
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


class PurchaseInvoiceDocumentResourceType(
    resources.PurchaseInvoiceDocumentResourceType, JournalDocumentResourceType
):
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
        kwargs["contact"] = _get_contact_from_moneybird_data(data)
        kwargs["total_price"] = data["total_price_incl_tax_base"]
        return kwargs

    @classmethod
    def get_document_line_model_kwargs(cls, line_data: MoneybirdResource, document):
        kwargs = super().get_document_line_model_kwargs(line_data, document)
        kwargs["amount"] = line_data["amount"]
        kwargs["tax_rate"] = _get_tax_rate_from_moneybird_data(line_data)
        kwargs["price"] = line_data["total_price_excl_tax_with_discount_base"]
        return kwargs


class ReceiptResourceType(resources.ReceiptResourceType, JournalDocumentResourceType):
    @classmethod
    def get_queryset(cls):
        return super().get_queryset().filter(document_kind=DocumentKind.RECEIPT)

    @classmethod
    def get_model_kwargs(cls, data):
        kwargs = super().get_model_kwargs(data)
        kwargs["document_kind"] = DocumentKind.RECEIPT
        kwargs["date"] = datetime.datetime.fromisoformat(data["date"]).date()
        kwargs["contact"] = _get_contact_from_moneybird_data(data)
        kwargs["total_price"] = data["total_price_incl_tax_base"]
        return kwargs

    @classmethod
    def get_document_line_model_kwargs(cls, line_data: MoneybirdResource, document):
        kwargs = super().get_document_line_model_kwargs(line_data, document)
        kwargs["amount"] = line_data["amount"]
        kwargs["tax_rate"] = _get_tax_rate_from_moneybird_data(line_data)
        kwargs["price"] = line_data["total_price_excl_tax_with_discount_base"]
        return kwargs


class GeneralJournalDocumentResourceType(
    resources.GeneralJournalDocumentResourceType, JournalDocumentResourceType
):
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


class ContactResourceType(resources.ContactResourceType):
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


class ProductResourceType(resources.ProductResourceType):
    model = Product

    @classmethod
    def get_model_kwargs(cls, data):
        kwargs = super().get_model_kwargs(data)
        kwargs["moneybird_json"] = data
        return kwargs


class ProjectResourceType(resources.ProjectResourceType):
    model = Project

    @classmethod
    def get_model_kwargs(cls, data):
        kwargs = super().get_model_kwargs(data)
        kwargs["moneybird_json"] = data
        return kwargs


class LedgerAccountResourceType(resources.LedgerAccountResourceType):
    model = Ledger

    @classmethod
    def get_model_kwargs(cls, data):
        kwargs = super().get_model_kwargs(data)
        kwargs["name"] = data["name"]
        kwargs["account_type"] = data["account_type"]
        return kwargs


class TaxRateResourceType(resources.TaxRateResourceType):
    model = TaxRate

    @classmethod
    def get_model_kwargs(cls, data):
        kwargs = super().get_model_kwargs(data)
        kwargs["moneybird_json"] = data
        return kwargs


class EstimateResourceType(resources.EstimateResourceType):
    model = Estimate
    document_lines_model = EstimateDocumentLine
    document_lines_foreign_key = "document_lines"
    document_foreign_key = "document"

    @classmethod
    def get_model_kwargs(cls, data):
        kwargs = super().get_model_kwargs(data)
        kwargs["moneybird_json"] = data
        kwargs["contact"] = _get_contact_from_moneybird_data(data)
        kwargs["workflow"] = _get_workflow_from_moneybird_data(data)
        kwargs["total_price"] = data["total_price_incl_tax_base"]

        return kwargs

    @classmethod
    def get_document_line_model_kwargs(cls, line_data: MoneybirdResource, document):
        kwargs = super().get_document_line_model_kwargs(line_data, document)
        kwargs["document"] = document
        kwargs["moneybird_json"] = line_data
        return kwargs


class RecurringSalesInvoiceResourceType(resources.RecurringSalesInvoiceResourceType):
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
        kwargs["contact"] = _get_contact_from_moneybird_data(data)
        kwargs["workflow"] = _get_workflow_from_moneybird_data(data)
        kwargs["total_price"] = data["total_price_incl_tax_base"]

        return kwargs

    @classmethod
    def get_document_line_model_kwargs(cls, line_data: MoneybirdResource, document):
        kwargs = super().get_document_line_model_kwargs(line_data, document)
        kwargs["document"] = document
        kwargs["moneybird_json"] = line_data
        return kwargs


class WorkflowResourceType(resources.WorkflowResourceType):
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
#     def get_model_kwargs(cls, resource_data):
#         kwargs = super().get_model_kwargs(resource_data)
#         kwargs["moneybird_json"] = resource_data
#         return kwargs
# TODO this can only be queried with contact id

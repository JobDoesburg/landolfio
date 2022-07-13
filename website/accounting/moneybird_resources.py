from decimal import Decimal

from django.db.models.functions import datetime

from accounting.models import (
    Contact,
    DocumentKind,
    JournalDocument,
    Subscription,
    Product,
    Ledger,
    Estimate,
    RecurringSalesInvoice,
    Workflow,
    LedgerAccountType,
    JournalDocumentLine,
    EstimateDocumentLine,
    RecurringSalesInvoiceDocumentLine,
    Project,
    TaxRate,
    DocumentStyle,
)
from moneybird.models import get_from_moneybird_data

from moneybird.resource_types import (
    MoneybirdResourceId,
    MoneybirdResource,
    MoneybirdResourceTypeWithDocumentLines,
)
from moneybird import resources


def _get_workflow_from_moneybird_data(data: MoneybirdResource):
    return get_from_moneybird_data(Workflow, data["workflow_id"])


def _get_ledger_from_moneybird_data(data: MoneybirdResource):
    return get_from_moneybird_data(Ledger, data["ledger_id"])


def _get_project_from_moneybird_data(data: MoneybirdResource):
    return get_from_moneybird_data(Project, data["project_id"])


def _get_product_from_moneybird_data(data: MoneybirdResource):
    return get_from_moneybird_data(Product, data["product_id"])


def _get_contact_from_moneybird_data(data: MoneybirdResource):
    return get_from_moneybird_data(Contact, data["contact_id"])


def _get_tax_rate_from_moneybird_data(data: MoneybirdResource):
    return get_from_moneybird_data(TaxRate, data["tax_rate_id"])


def _get_recurring_sales_invoice_from_moneybird_data(data: MoneybirdResource):
    return get_from_moneybird_data(
        RecurringSalesInvoice, data["recurring_sales_invoice_id"]
    )


def _get_document_style_from_moneybird_data(data: MoneybirdResource):
    return get_from_moneybird_data(DocumentStyle, data["document_style_id"])


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
        data = super().serialize_for_moneybird(instance)
        data["company_name"] = instance.company_name
        data["firstname"] = instance.first_name
        data["lastname"] = instance.last_name
        data["send_invoices_to_email"] = instance.email
        data["send_estimates_to_email"] = instance.email
        return data


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


class DocumentStyleResourceType(resources.DocumentStyleResourceType):
    model = DocumentStyle

    @classmethod
    def get_model_kwargs(cls, resource_data):
        kwargs = super().get_model_kwargs(resource_data)
        kwargs["moneybird_json"] = resource_data
        return kwargs


class WorkflowResourceType(resources.WorkflowResourceType):
    model = Workflow

    @classmethod
    def get_model_kwargs(cls, resource_data):
        kwargs = super().get_model_kwargs(resource_data)
        kwargs["name"] = resource_data["name"]
        return kwargs


class SubscriptionResourceType(resources.SubscriptionResourceType):
    model = Subscription
    parameter_resource_type = ContactResourceType

    @classmethod
    def get_model_kwargs(cls, resource_data):
        kwargs = super().get_model_kwargs(resource_data)
        kwargs["moneybird_json"] = resource_data
        kwargs["reference"] = resource_data["reference"]
        kwargs["start_date"] = resource_data["start_date"]
        kwargs["end_date"] = resource_data["end_date"]
        kwargs["cancelled_at"] = resource_data["cancelled_at"]
        kwargs["frequency"] = resource_data["frequency"]
        kwargs["frequency_type"] = resource_data["frequency_type"]
        # kwargs["document_style"] = _get_document_style_from_moneybird_data(resource_data) # TODO this is received via the recurring sales invoice
        kwargs["contact"] = _get_contact_from_moneybird_data(resource_data)
        kwargs["product"] = _get_product_from_moneybird_data(resource_data)
        kwargs[
            "recurring_sales_invoice"
        ] = _get_recurring_sales_invoice_from_moneybird_data(resource_data)
        return kwargs

    @classmethod
    def serialize_for_moneybird(cls, instance):
        data = super().serialize_for_moneybird(instance)

        data["start_date"] = instance.start_date.isoformat()
        data["product"] = MoneybirdResourceId(instance.product.moneybird_id)
        data["contact"] = MoneybirdResourceId(instance.contact.moneybird_id)
        if data.end_date:
            data["start_date"] = instance.end_date.isoformat()
        data["reference"] = instance.reference
        data["document_style_id"] = MoneybirdResourceId(
            instance.document_style.moneybird_id
        )
        data["frequency"] = instance.frequency
        data["frequency_type"] = instance.frequency_type

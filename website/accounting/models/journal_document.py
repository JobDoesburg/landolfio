import datetime
from decimal import Decimal

from django.db import models
from django.utils.translation import gettext as _

from accounting.models.contact import Contact, ContactResourceType
from accounting.models.ledger_account import (
    LedgerAccount,
    LedgerAccountType,
    LedgerAccountResourceType,
)
from accounting.models.product import Product
from accounting.models.project import Project, ProjectResourceType
from accounting.models.tax_rate import TaxRate, TaxRateResourceType
from accounting.models.workflow import Workflow, WorkflowResourceType
from moneybird import resources
from moneybird.models import (
    SynchronizableMoneybirdResourceModel,
    MoneybirdDocumentLineModel,
    get_or_create_from_moneybird_data,
)
from moneybird.resource_types import (
    MoneybirdResourceTypeWithDocumentLines,
    MoneybirdResource,
    MoneybirdResourceId,
)


class DocumentKind(models.TextChoices):
    SALES_INVOICE = "FAC", _("Sales invoice")
    PURCHASE_INVOICE = "INK", _("Purchase invoice")
    RECEIPT = "BON", _("Receipt")
    GENERAL_JOURNAL_DOCUMENT = "MEM", _("General journal document")


class JournalDocument(SynchronizableMoneybirdResourceModel):
    date = models.DateField(null=True, verbose_name=_("Date"))
    moneybird_json = models.JSONField(verbose_name=_("JSON MoneyBird"), null=True)
    document_kind = models.CharField(
        max_length=3, choices=DocumentKind.choices, verbose_name=_("document kind")
    )
    reference = models.CharField(
        max_length=150, null=True, blank=True, verbose_name=_("reference")
    )
    contact = models.ForeignKey(
        Contact,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Contact"),
        related_name="journal_documents",
    )
    workflow = models.ForeignKey(
        Workflow, null=True, on_delete=models.SET_NULL, verbose_name=_("Workflow")
    )
    total_price = models.DecimalField(
        max_digits=19, decimal_places=2, verbose_name=_("total price"), null=True
    )
    total_paid = models.DecimalField(
        max_digits=19, decimal_places=2, verbose_name=_("total paid"), null=True
    )

    total_unpaid = models.DecimalField(
        max_digits=19, decimal_places=2, verbose_name=_("total unpaid"), null=True
    )

    def __str__(self):
        if self.document_kind == DocumentKind.SALES_INVOICE:
            if self.moneybird_json["invoice_id"] is not None:
                return f"{self.document_kind} {self.moneybird_json['invoice_id']}"
            return (
                f"{self.document_kind} {_('draft')} {self.moneybird_json['draft_id']}"
            )
        else:
            return f"{self.document_kind} {self.moneybird_json['reference']}"

    class Meta:
        unique_together = ("moneybird_id", "document_kind")
        verbose_name = _("Journal document")
        verbose_name_plural = _("Journal documents")
        ordering = ("-date",)


class JournalDocumentLine(MoneybirdDocumentLineModel):
    moneybird_json = models.JSONField(verbose_name=_("JSON MoneyBird"), null=True)
    description = models.TextField(verbose_name=_("Description"), null=True, blank=True)
    amount = models.CharField(
        verbose_name=_("Amount"), null=True, blank=True, default="1 x", max_length=10
    )
    ledger = models.ForeignKey(
        LedgerAccount,
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
        verbose_name=_("Ledger"),
    )

    project = models.ForeignKey(
        Project,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Project"),
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Product"),
    )

    tax_rate = models.ForeignKey(
        TaxRate,
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
        verbose_name=_("Tax rate"),
    )

    price = models.DecimalField(
        max_digits=19, decimal_places=2, verbose_name=_("Price")
    )
    document = models.ForeignKey(
        JournalDocument,
        on_delete=models.CASCADE,
        verbose_name=_("Document"),
        related_name="document_lines",
    )
    asset_id_field = models.CharField(
        max_length=50, null=True, blank=True, verbose_name=_("Asset Id")
    )
    asset = models.ForeignKey(
        "inventory.Asset",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Asset"),
        related_name="journal_document_lines",
    )

    def __str__(self):
        return f"Line in {self.document} with asset {self.asset_id}"

    class Meta:
        verbose_name = _("Journal document line")
        verbose_name_plural = _("Journal document lines")
        ordering = ("-document__date",)


class JournalDocumentResourceType(MoneybirdResourceTypeWithDocumentLines):
    model = JournalDocument
    document_lines_model = JournalDocumentLine
    document_lines_foreign_key = "document_lines"
    document_foreign_key = "document"

    @classmethod
    def get_model_kwargs(cls, data):
        kwargs = super().get_model_kwargs(data)
        kwargs["moneybird_json"] = data
        kwargs["reference"] = data["reference"]
        return kwargs

    @classmethod
    def get_document_line_model_kwargs(cls, line_data: MoneybirdResource, document):
        kwargs = super().get_document_line_model_kwargs(line_data, document)
        kwargs["document"] = document
        kwargs["description"] = line_data["description"]
        kwargs["ledger"] = get_or_create_from_moneybird_data(
            LedgerAccountResourceType, line_data["ledger_account_id"]
        )
        kwargs["project"] = get_or_create_from_moneybird_data(
            ProjectResourceType, line_data["project_id"]
        )
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
        # kwargs["date"] = datetime.datetime.fromisoformat(data["invoice_date"]).date()
        kwargs["contact"] = get_or_create_from_moneybird_data(
            ContactResourceType, data["contact_id"]
        )
        kwargs["workflow"] = get_or_create_from_moneybird_data(
            WorkflowResourceType, data["workflow_id"]
        )
        kwargs["total_price"] = data["total_price_incl_tax_base"]
        kwargs["total_paid"] = data["total_paid"]
        kwargs["total_unpaid"] = data["total_unpaid"]
        return kwargs

    @classmethod
    def get_document_line_model_kwargs(cls, line_data: MoneybirdResource, document):
        kwargs = super().get_document_line_model_kwargs(line_data, document)
        kwargs["amount"] = line_data["amount"]
        kwargs["tax_rate"] = get_or_create_from_moneybird_data(
            TaxRateResourceType, line_data["tax_rate_id"]
        )
        ledger = kwargs["ledger"]
        kwargs["price"] = line_data["total_price_excl_tax_with_discount_base"]
        if (
            ledger
            and ledger.account_type
            and ledger.account_type == LedgerAccountType.NON_CURRENT_ASSETS
        ):
            kwargs["price"] = -1 * Decimal(kwargs["price"])  # TODO is dit handig?
        return kwargs

    @classmethod
    def serialize_for_moneybird(cls, instance):
        data = super().serialize_for_moneybird(instance)
        if instance.date:
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
        kwargs["contact"] = get_or_create_from_moneybird_data(
            ContactResourceType, data["contact_id"]
        )
        kwargs["total_price"] = data["total_price_incl_tax_base"]
        return kwargs

    @classmethod
    def get_document_line_model_kwargs(cls, line_data: MoneybirdResource, document):
        kwargs = super().get_document_line_model_kwargs(line_data, document)
        kwargs["amount"] = line_data["amount"]
        kwargs["tax_rate"] = get_or_create_from_moneybird_data(
            TaxRateResourceType, line_data["tax_rate_id"]
        )
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
        kwargs["contact"] = get_or_create_from_moneybird_data(
            ContactResourceType, data["contact_id"]
        )
        kwargs["total_price"] = data["total_price_incl_tax_base"]
        return kwargs

    @classmethod
    def get_document_line_model_kwargs(cls, line_data: MoneybirdResource, document):
        kwargs = super().get_document_line_model_kwargs(line_data, document)
        kwargs["amount"] = line_data["amount"]
        kwargs["tax_rate"] = get_or_create_from_moneybird_data(
            TaxRateResourceType, line_data["tax_rate_id"]
        )
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

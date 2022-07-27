import datetime
from decimal import Decimal

from django.db import models
from django.utils.translation import gettext as _

from accounting.models.contact import Contact, ContactResourceType
from accounting.models.document_style import DocumentStyle, DocumentStyleResourceType
from accounting.models.journal_document import (
    JournalDocumentLine,
    JournalDocumentResourceType,
)
from accounting.models.ledger_account import LedgerAccountType
from accounting.models.product import Product, ProductResourceType
from accounting.models.recurring_sales_invoice import (
    RecurringSalesInvoice,
    RecurringSalesInvoiceResourceType,
)
from accounting.models.tax_rate import TaxRateResourceType, TaxRate, TaxRateTypes
from accounting.models.workflow import Workflow, WorkflowResourceType, WorkflowTypes
from moneybird import resources
from moneybird.models import (
    SynchronizableMoneybirdResourceModel,
)
from moneybird.resource_types import MoneybirdResource, MoneybirdResourceId


class PurchaseDocumentKind(models.TextChoices):
    PURCHASE_INVOICE = "INK", _("Purchase invoice")
    RECEIPT = "BON", _("Receipt")


class PurchaseDocumentStates(models.TextChoices):
    OPEN = "open", _("open")
    SCHEDULED = "scheduled", _("scheduled")
    PENDING_PAYMENT = "pending_payment", _("pending payment")
    LATE = "late", _("late")
    PAID = "paid", _("paid")


class PurchaseDocument(SynchronizableMoneybirdResourceModel):
    document_kind = models.CharField(
        max_length=3,
        choices=PurchaseDocumentKind.choices,
        verbose_name=_("document kind"),
    )
    contact = models.ForeignKey(
        Contact,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Contact"),
        related_name="purchase_documents",
    )

    total_price = models.DecimalField(
        max_digits=19, decimal_places=2, verbose_name=_("total price"), null=True
    )
    state = models.CharField(
        max_length=30,
        null=False,
        blank=False,
        choices=PurchaseDocumentStates.choices,
        default=PurchaseDocumentStates.OPEN,
        verbose_name=_("state"),
    )
    date = models.DateField(null=True, blank=True, verbose_name=_("date"))
    due_date = models.DateField(null=True, blank=True, verbose_name=_("due date"))
    reference = models.CharField(
        max_length=255, null=True, blank=False, verbose_name=_("reference")
    )
    paid_at = models.DateField(null=True, verbose_name=_("paid at"))
    prices_are_incl_tax = models.BooleanField(
        default=True, verbose_name=_("prices are incl. tax")
    )

    def __str__(self):
        return f"{self.document_kind} {self.reference}"

    class Meta:
        verbose_name = _("Purchase document")
        verbose_name_plural = _("Purchase documents")
        ordering = ("-date",)


class PurchaseDocumentLine(JournalDocumentLine):
    amount = models.CharField(
        verbose_name=_("Amount"), null=True, blank=True, default="1 x", max_length=10
    )
    amount_decimal = models.DecimalField(
        null=True,
        max_digits=19,
        decimal_places=2,
        blank=True,
        verbose_name=_("Amount (decimal)"),
    )
    price = models.DecimalField(
        max_digits=19, decimal_places=2, verbose_name=_("price")
    )
    document = models.ForeignKey(
        PurchaseDocument,
        on_delete=models.CASCADE,
        verbose_name=_("Document"),
        related_name="document_lines",
    )
    tax_rate = models.ForeignKey(
        TaxRate,
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
        verbose_name=_("Tax rate"),
        limit_choices_to={"active": True, "type": TaxRateTypes.PURCHASE_INVOICE},
    )
    row_order = models.PositiveSmallIntegerField(
        null=True, blank=True, verbose_name=_("row order")
    )

    def __str__(self):
        return f"{self.amount} {self.description} in {self.document}"

    class Meta:
        verbose_name = _("Purchase document line")
        verbose_name_plural = _("Purchase document lines")
        ordering = ("-document__date", "row_order")


class PurchaseInvoiceDocumentResourceType(
    resources.PurchaseInvoiceDocumentResourceType, JournalDocumentResourceType
):
    model = PurchaseDocument
    document_lines_model = PurchaseDocumentLine

    @classmethod
    def get_queryset(cls):
        return (
            super()
            .get_queryset()
            .filter(document_kind=PurchaseDocumentKind.PURCHASE_INVOICE)
        )

    @classmethod
    def get_model_kwargs(cls, data):
        kwargs = super().get_model_kwargs(data)
        kwargs["document_kind"] = PurchaseDocumentKind.PURCHASE_INVOICE
        kwargs["contact"] = ContactResourceType.get_or_create_from_moneybird_data(
            data["contact_id"]
        )
        kwargs["date"] = datetime.datetime.fromisoformat(data["date"]).date()
        if data["due_date"]:
            kwargs["due_date"] = datetime.datetime.fromisoformat(
                data["due_date"]
            ).date()
        kwargs["total_price"] = data["total_price_incl_tax_base"]
        kwargs["reference"] = data["reference"]
        if data["paid_at"]:
            kwargs["paid_at"] = datetime.datetime.fromisoformat(data["paid_at"]).date()
        kwargs["state"] = data["state"]
        kwargs["prices_are_incl_tax"] = data["prices_are_incl_tax"]
        return kwargs

    @classmethod
    def get_document_line_model_kwargs(cls, line_data: MoneybirdResource, document):
        kwargs = super().get_document_line_model_kwargs(line_data, document)
        kwargs["document"] = document
        kwargs["amount"] = line_data["amount"]
        kwargs["amount_decimal"] = line_data["amount_decimal"]
        kwargs["row_order"] = line_data["row_order"]
        kwargs["price"] = line_data["price"]
        kwargs["tax_rate"] = TaxRateResourceType.get_or_create_from_moneybird_data(
            line_data["tax_rate_id"]
        )
        ledger_account = kwargs["ledger_account"]
        kwargs["total_amount"] = line_data["total_price_excl_tax_with_discount_base"]
        if (
            ledger_account
            and ledger_account.account_type
            and ledger_account.account_type == LedgerAccountType.NON_CURRENT_ASSETS
        ):
            kwargs["total_amount"] = -1 * Decimal(
                kwargs["total_amount"]
            )  # TODO is dit handig?
        return kwargs

    @classmethod
    def serialize_for_moneybird(cls, instance):
        data = super().serialize_for_moneybird(instance)
        if instance.contact:
            data["contact_id"] = MoneybirdResourceId(instance.contact.moneybird_id)

        if instance.date:
            data["date"] = instance.date.isoformat()
        if instance.due_date:
            data["due_date"] = instance.due_date.isoformat()

        data["reference"] = instance.reference
        data["prices_are_incl_tax"] = instance.prices_are_incl_tax
        return data

    @classmethod
    def serialize_document_line_for_moneybird(cls, document_line, document):
        data = super().serialize_document_line_for_moneybird(document_line, document)
        data["amount"] = document_line.amount
        data["description"] = document_line.description
        data["row_order"] = document_line.row_order
        data["price"] = float(document_line.price)
        data["tax_rate_id"] = document_line.tax_rate.moneybird_id
        if document_line.ledger_account:
            data["ledger_account_id"] = MoneybirdResourceId(
                document_line.ledger_account.moneybird_id
            )
            if (
                document_line.ledger_account.account_type
                and document_line.ledger_account.account_type
                == LedgerAccountType.NON_CURRENT_ASSETS
            ):
                data["price"] = float(-1 * document_line.price)  # TODO is dit handig?
        return data


class ReceiptResourceType(PurchaseInvoiceDocumentResourceType):
    @classmethod
    def get_queryset(cls):
        return super().get_queryset().filter(document_kind=PurchaseDocumentKind.RECEIPT)

    @classmethod
    def get_model_kwargs(cls, data):
        kwargs = super().get_model_kwargs(data)
        kwargs["document_kind"] = PurchaseDocumentKind.RECEIPT
        return kwargs

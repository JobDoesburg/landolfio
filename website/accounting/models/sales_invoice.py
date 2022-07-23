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
from accounting.models.tax_rate import TaxRateResourceType, TaxRate
from accounting.models.workflow import Workflow, WorkflowResourceType, WorkflowTypes
from moneybird import resources
from moneybird.models import (
    SynchronizableMoneybirdResourceModel,
)
from moneybird.resource_types import MoneybirdResource, MoneybirdResourceId


class SalesInvoiceStates(models.TextChoices):
    DRAFT = "draft", _("draft")
    OPEN = "open", _("open")
    SCHEDULED = "scheduled", _("scheduled")
    PENDING_PAYMENT = "pending_payment", _("pending payment")
    LATE = "late", _("late")
    PAID = "paid", _("paid")
    UNCOLLECTIBLE = "uncollectible", _("uncollectible")


class SalesInvoice(SynchronizableMoneybirdResourceModel):
    contact = models.ForeignKey(
        Contact,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Contact"),
        related_name="sales_invoices",
    )
    # TODO: contact person
    invoice_id = models.CharField(
        max_length=255, null=True, blank=True, verbose_name=_("invoice id")
    )
    draft_id = models.CharField(
        max_length=255, null=True, blank=True, verbose_name=_("draft id")
    )
    recurring_sales_invoice = models.ForeignKey(
        RecurringSalesInvoice, on_delete=models.SET_NULL, null=True, blank=True
    )
    workflow = models.ForeignKey(
        Workflow,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={"active": True, "type": WorkflowTypes.INVOICE_WORKFLOW},
        verbose_name=_("Workflow"),
    )
    document_style = models.ForeignKey(
        DocumentStyle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Document style"),
    )

    total_price = models.DecimalField(
        max_digits=19, decimal_places=2, verbose_name=_("total price"), null=True
    )
    state = models.CharField(
        max_length=30,
        null=False,
        blank=False,
        choices=SalesInvoiceStates.choices,
        default=SalesInvoiceStates.DRAFT,
        verbose_name=_("state"),
    )
    invoice_date = models.DateField(
        null=True, blank=True, verbose_name=_("invoice date")
    )
    due_date = models.DateField(null=True, blank=True, verbose_name=_("due date"))
    payment_conditions = models.TextField(
        null=True, blank=True, verbose_name=_("payment conditions")
    )
    payment_reference = models.CharField(
        max_length=255, null=True, verbose_name=_("payment reference")
    )
    reference = models.CharField(
        max_length=255, null=True, blank=True, verbose_name=_("reference")
    )
    discount = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("discount"),
    )
    original_sales_invoice = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("original sales invoice"),
    )
    paused = models.BooleanField(default=False, verbose_name=_("paused"))
    paid_at = models.DateField(null=True, verbose_name=_("paid at"))
    sent_at = models.DateField(null=True, verbose_name=_("sent at"))
    public_view_code = models.CharField(
        max_length=10, null=True, verbose_name=_("public view code")
    )
    total_paid = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, verbose_name=_("total paid")
    )
    total_unpaid = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, verbose_name=_("total unpaid")
    )
    url = models.URLField(null=True, verbose_name=_("url"))
    payment_url = models.URLField(null=True, verbose_name=_("payment url"))
    prices_are_incl_tax = models.BooleanField(default=True, verbose_name=_("prices are incl. tax"))

    def __str__(self):
        if self.draft_id:
            return f"Draft {self.draft_id}"
        return f"{self.invoice_id}"

    class Meta:
        verbose_name = _("Sales invoice")
        verbose_name_plural = _("Sales invoices")
        ordering = ("-invoice_date",)


class SalesInvoiceDocumentLine(JournalDocumentLine):
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
        SalesInvoice,
        on_delete=models.CASCADE,
        verbose_name=_("Document"),
        related_name="document_lines",
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
    row_order = models.PositiveSmallIntegerField(null=True, verbose_name=_("row order"))

    def __str__(self):
        return f"{self.amount} {self.description} in {self.document}"

    class Meta:
        verbose_name = _("Sales invoice document line")
        verbose_name_plural = _("Sales invoice document lines")
        ordering = ("-document__invoice_date", "row_order")


class SalesInvoiceResourceType(
    resources.SalesInvoiceResourceType, JournalDocumentResourceType
):
    model = SalesInvoice
    document_lines_model = SalesInvoiceDocumentLine

    @classmethod
    def get_model_kwargs(cls, data):
        kwargs = super().get_model_kwargs(data)
        kwargs["contact"] = ContactResourceType.get_or_create_from_moneybird_data(
            data["contact_id"]
        )
        kwargs[
            "recurring_sales_invoice"
        ] = RecurringSalesInvoiceResourceType.get_or_create_from_moneybird_data(
            data["recurring_sales_invoice_id"]
        )
        kwargs["workflow"] = WorkflowResourceType.get_or_create_from_moneybird_data(
            data["workflow_id"]
        )
        kwargs[
            "document_style"
        ] = DocumentStyleResourceType.get_or_create_from_moneybird_data(
            data["document_style_id"]
        )
        kwargs[
            "original_sales_invoice"
        ] = SalesInvoiceResourceType.get_or_create_from_moneybird_data(
            data["original_sales_invoice_id"]
        )
        kwargs["invoice_id"] = data["invoice_id"]
        kwargs["draft_id"] = data["draft_id"]
        if data["invoice_date"]:
            kwargs["invoice_date"] = datetime.datetime.fromisoformat(
                data["invoice_date"]
            ).date()
        kwargs["due_date"] = datetime.datetime.fromisoformat(data["due_date"]).date()
        kwargs["payment_conditions"] = data["payment_conditions"]
        kwargs["payment_reference"] = data["payment_reference"]
        kwargs["total_price"] = data["total_price_incl_tax_base"]
        kwargs["reference"] = data["reference"]
        kwargs["discount"] = data["discount"]
        kwargs["paused"] = data["paused"]
        if data["paid_at"]:
            kwargs["paid_at"] = datetime.datetime.fromisoformat(data["paid_at"]).date()
        kwargs["sent_at"] = data["sent_at"]
        kwargs["state"] = data["state"]
        kwargs["public_view_code"] = data["public_view_code"]
        kwargs["total_paid"] = data["total_paid"]
        kwargs["total_unpaid"] = data["total_unpaid"]
        kwargs["url"] = data["url"]
        kwargs["payment_url"] = data["payment_url"]
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
        kwargs["product"] = ProductResourceType.get_or_create_from_moneybird_data(
            line_data["product_id"]
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
        if instance.workflow:
            data["workflow_id"] = MoneybirdResourceId(instance.workflow.moneybird_id)
        if instance.document_style:
            data["document_style_id"] = MoneybirdResourceId(
                instance.document_style.moneybird_id
            )
        if instance.due_date:
            data["due_date"] = instance.due_date.isoformat()
        if instance.invoice_date:
            data["invoice_date"] = instance.invoice_date.isoformat()
        data["payment_conditions"] = instance.payment_conditions
        data["reference"] = instance.reference or ""
        data["discount"] = instance.discount
        data["paused"] = instance.paused
        data["prices_are_incl_tax"] = instance.prices_are_incl_tax
        return data

    @classmethod
    def serialize_document_line_for_moneybird(cls, document_line, document):
        data = super().serialize_document_line_for_moneybird(document_line, document)
        data["description"] = document_line.description
        data["row_order"] = document_line.row_order
        data["price"] = float(document_line.price)
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

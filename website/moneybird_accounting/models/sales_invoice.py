from django.db import models
from django.db.models import PROTECT, CASCADE

from moneybird_accounting.models.project import Project
from moneybird_accounting.models.product import Product
from moneybird_accounting.models.ledger_account import LedgerAccount
from moneybird_accounting.models.tax_rate import TaxRate
from moneybird_accounting.models.workflow import Workflow
from moneybird_accounting.models.contact import Contact
from moneybird_accounting.models.moneybird_resource import (
    MoneybirdNestedDataResourceModel,
    MoneybirdSynchronizableResourceModel,
)


class InvoiceDetailItem(MoneybirdNestedDataResourceModel):
    class Meta:
        verbose_name = "invoice detail item"
        verbose_name_plural = "invoice detail items"

    moneybird_resource_name = "details"

    moneybird_data_fields = [
        "invoice_id",
        "tax_rate_id",
        "ledger_account_id",
        "project_id",
        "product_id",
        "amount",
        "amount_decimal",
        "description",
        "price",
        "period",
        "row_order",
        "total_price_excl_tax_with_discount",
        "total_price_excl_tax_with_discount_base",
    ]

    moneybird_nested_foreign_key = "invoice"

    invoice = models.ForeignKey(
        "SalesInvoice", related_name="details", null=False, blank=False, on_delete=CASCADE, db_constraint=False
    )  # db_constraint must be false to prevent integrity errors on sync, where objects are created without the parent yet existing

    tax_rate = models.ForeignKey(TaxRate, blank=True, null=True, on_delete=PROTECT)
    ledger_account = models.ForeignKey(LedgerAccount, blank=True, null=True, on_delete=PROTECT)
    project = models.ForeignKey(Project, blank=True, null=True, on_delete=PROTECT)
    product = models.ForeignKey(Product, blank=True, null=True, on_delete=PROTECT)

    amount = models.CharField(blank=True, null=True, max_length=10)
    amount_decimal = models.DecimalField(blank=True, null=True, max_digits=10, decimal_places=2)
    description = models.CharField(blank=True, null=True, max_length=1000)
    price = models.DecimalField(blank=True, null=True, max_digits=10, decimal_places=2)

    period = models.CharField(
        blank=True,
        null=True,
        max_length=100,
        help_text="Allowed input format: yyyymmdd..yyyymmdd, OR 'this_month', 'prev_month', 'next_month'.",
    )
    row_order = models.PositiveSmallIntegerField(null=True, blank=True)

    total_price_excl_tax_with_discount = models.DecimalField(blank=True, null=True, max_digits=10, decimal_places=2)
    total_price_excl_tax_with_discount_base = models.DecimalField(
        blank=True, null=True, max_digits=10, decimal_places=2
    )

    def __str__(self):
        return f"Invoice item {self.invoice}: {self.description} ({self.amount} {self.price})"


class SalesInvoice(MoneybirdSynchronizableResourceModel):
    class Meta:
        verbose_name = "sales invoice"
        verbose_name_plural = "sales invoices"

    moneybird_resource_path_name = "sales_invoices"
    moneybird_resource_name = "sales_invoice"

    moneybird_data_fields = [
        "invoice_id",
        "draft_id",
        "contact_id",
        "workflow_id",
        "state",
        "reference",
        "invoice_date",
        "due_date",
        "first_due_interval",
        "discount",
        "paused",
        "paid_at",
        "sent_at",
        "url",
        "original_sales_invoice_id",
        "payment_url",
        "payment_conditions",
        "payment_reference",
        "public_view_code",
        "total_paid",
        "total_unpaid",
        "total_unpai" "d_base",
        "total_price_excl_tax",
        "total_price_excl_tax_base",
        "total_price_incl_tax",
        "total_price_incl_tax_base",
        "total_discount",
        "prices_are_incl_tax",
    ]
    moneybird_readonly_data_fields = [
        "invoice_id",
        "draft_id",
        "due_date",
        "state",
        "paused",
        "paid_at",
        "sent_at",
        "payment_reference",
        "public_view_code",
        "original_sales_invoice_id",
        "url",
        "payment_url",
        "total_paid",
        "total_unpaid",
        "total_unpaid_base",
        "total_price_excl_tax",
        "total_price_excl_tax_base",
        "total_price_incl_tax",
        "total_price_incl_tax_base",
        "total_discount",
    ]
    moneybird_foreign_key_fields = ["contact"]
    moneybird_nested_data_fields = {
        "details": InvoiceDetailItem,
    }

    # TODO include recurring_sales_invoice_id

    invoice_id = models.CharField(unique=True, blank=True, null=True, max_length=20)
    draft_id = models.CharField(unique=True, blank=True, null=True, max_length=20)

    contact = models.ForeignKey(Contact, blank=False, null=False, on_delete=PROTECT, db_constraint=False)

    workflow = models.ForeignKey(
        Workflow,
        blank=True,
        null=True,
        on_delete=PROTECT,
        limit_choices_to={"type": Workflow.WORKFLOW_TYPE_INVOICE_WORKFLOW},
    )

    STATE_DRAFT = "draft"
    STATE_OPEN = "open"
    STATE_SCHEDULED = "scheduled"
    STATE_PENDING_PAYMENT = "pending_payment"
    STATE_LATE = "late"
    STATE_REMINDED = "reminded"
    STATE_PAID = "paid"
    STATE_UNCOLLECTIBLE = "uncollectible"
    INVOICE_STATES = (
        (STATE_DRAFT, "Draft"),
        (STATE_OPEN, "Open"),
        (STATE_SCHEDULED, "Scheduled"),
        (STATE_PENDING_PAYMENT, "Pending payment"),
        (STATE_LATE, "Late"),
        (STATE_REMINDED, "Reminded"),
        (STATE_PAID, "Paid"),
        (STATE_UNCOLLECTIBLE, "Uncollectible"),
    )

    # TODO add help texts

    state = models.CharField(blank=True, null=True, choices=INVOICE_STATES, max_length=100)

    reference = models.CharField(blank=True, null=True, max_length=1000)
    invoice_date = models.DateField(blank=True, null=True, help_text="Will be set automatically when invoice is sent.")
    first_due_interval = models.IntegerField(blank=True, null=True)
    due_date = models.DateField(blank=True, null=True)

    discount = models.DecimalField(blank=True, null=True, max_digits=5, decimal_places=2)

    paused = models.BooleanField(blank=False, null=False, default=False)  # Make readonly, add action
    paid_at = models.DateField(blank=True, null=True)
    sent_at = models.DateField(blank=True, null=True)

    original_sales_invoice = models.ForeignKey("self", null=True, blank=True, on_delete=CASCADE, db_constraint=False)
    payment_conditions = models.TextField(
        blank=True, null=True, help_text="Supports Moneybird tags in the form of {document.field}."
    )
    payment_reference = models.CharField(blank=True, null=True, max_length=100)
    public_view_code = models.CharField(blank=True, null=True, max_length=100)
    url = models.CharField(blank=True, null=True, max_length=1000)
    payment_url = models.CharField(blank=True, null=True, max_length=1000)

    total_paid = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2)
    total_unpaid = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2)
    total_unpaid_base = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2)
    total_price_excl_tax = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2)
    total_price_excl_tax_base = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2)
    total_price_incl_tax = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2)
    total_price_incl_tax_base = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2)
    total_discount = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2)
    prices_are_incl_tax = models.BooleanField(default=True, verbose_name="display prices incl. tax")

    # TODO pdf?

    @property
    def number_of_rows(self):
        return len(self.details.all())

    def __str__(self):
        if self.state == SalesInvoice.STATE_DRAFT:
            return f"Draft {self.draft_id}"
        else:
            return f"{self.invoice_id}"

    def send(self):
        pass
        # post to "pause"

    def pause(self):
        pass
        # post to "resume"

    def send_reminder(self):
        pass
        # post to "resume"1

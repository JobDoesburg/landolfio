from django.db import models
from django.db.models import CASCADE, PROTECT

from moneybird_accounting.models.project import Project
from moneybird_accounting.models.product import Product
from moneybird_accounting.models.ledger_account import LedgerAccount
from moneybird_accounting.models.workflow import Workflow
from moneybird_accounting.models.tax_rate import TaxRate
from moneybird_accounting.models.contact import Contact
from moneybird_accounting.models.moneybird_resource import (
    MoneybirdSynchronizableResourceModel,
    MoneybirdNestedDataResourceModel,
)


class RecurringInvoiceDetailItem(MoneybirdNestedDataResourceModel):
    class Meta:
        verbose_name = "recurring sales invoice detail item"
        verbose_name_plural = "recurring sales invoice detail items"

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
        "RecurringSalesInvoice",
        related_name="details",
        null=False,
        blank=False,
        on_delete=CASCADE,
        db_constraint=False,
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


class RecurringSalesInvoice(MoneybirdSynchronizableResourceModel):
    class Meta:
        verbose_name = "recurring sales invoice"
        verbose_name_plural = "recurring sales invoices"

    moneybird_resource_path_name = "recurring_sales_invoices"
    moneybird_resource_name = "recurring_sales_invoice"

    moneybird_data_fields = [
        "active",
        "auto_send",
        "mergeable",
        "has_desired_count",
        "desired_count",
        "frequency",
        "frequency_type",
        "start_date",
        "invoice_date",
        "last_date",
        "contact_id",
        "workflow_id",
        "reference",
        "first_due_interval",
        "discount",
        "payment_conditions",
        "total_price_excl_tax",
        "total_price_excl_tax_base",
        "total_price_incl_tax",
        "total_price_incl_tax_base",
        "total_discount",
        "prices_are_incl_tax",
    ]
    moneybird_readonly_data_fields = [
        "total_price_excl_tax",
        "total_price_excl_tax_base",
        "total_price_incl_tax",
        "total_price_incl_tax_base",
        "total_discount",
    ]
    moneybird_foreign_key_fields = ["contact"]
    moneybird_nested_data_fields = {
        "details": RecurringInvoiceDetailItem,
    }

    active = models.BooleanField(blank=True, null=True)
    auto_send = models.BooleanField(blank=True, null=True)
    # TODO think about sending_scheduled_at
    mergeable = models.BooleanField(blank=True, null=True)
    has_desired_count = models.BooleanField(blank=True, null=True)
    desired_count = models.PositiveIntegerField(blank=True, null=True)

    frequency = models.PositiveIntegerField(blank=True, null=True)

    FREQUENCY_TYPE_DAY = "day"
    FREQUENCY_TYPE_WEEK = "week"
    FREQUENCY_TYPE_MONTH = "month"
    FREQUENCY_TYPE_QUARTER = "quarter"
    FREQUENCY_TYPE_YEAR = "year"
    FREQUENCY_TYPE_CHOICES = (
        (FREQUENCY_TYPE_DAY, "Daily"),
        (FREQUENCY_TYPE_WEEK, "Weekly"),
        (FREQUENCY_TYPE_MONTH, "Monthly"),
        (FREQUENCY_TYPE_QUARTER, "Quarterly"),
        (FREQUENCY_TYPE_YEAR, "Annually"),
    )

    frequency_type = models.CharField(blank=True, null=True, choices=FREQUENCY_TYPE_CHOICES, max_length=20)

    contact = models.ForeignKey(Contact, blank=False, null=False, on_delete=PROTECT, db_constraint=False)

    start_date = models.DateField(blank=True, null=True)
    invoice_date = models.DateField(blank=True, null=True)
    last_date = models.DateField(blank=True, null=True)

    workflow = models.ForeignKey(
        Workflow,
        blank=True,
        null=True,
        on_delete=PROTECT,
        limit_choices_to={"type": Workflow.WORKFLOW_TYPE_INVOICE_WORKFLOW},
    )
    reference = models.CharField(blank=True, null=True, max_length=1000)
    first_due_interval = models.IntegerField(blank=True, null=True)

    discount = models.DecimalField(blank=True, null=True, max_digits=5, decimal_places=2)

    payment_conditions = models.TextField(
        blank=True, null=True, help_text="Supports Moneybird tags in the form of {document.field}."
    )  # TODO fix why this is empty (both here and in the other model)

    total_price_excl_tax = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2)
    total_price_excl_tax_base = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2)
    total_price_incl_tax = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2)
    total_price_incl_tax_base = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2)
    total_discount = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2)
    prices_are_incl_tax = models.BooleanField(default=True, verbose_name="display prices incl. tax")

    @property
    def number_of_rows(self):
        return len(self.details.all())

    def __str__(self):
        return f"Recurring sales invoice to {self.contact} ({self.total_price_incl_tax})"

import datetime
from decimal import Decimal

from django.db import models
from django.db.models import F
from django.utils.translation import gettext as _
from queryable_properties.properties import AnnotationProperty

from accounting.models.ledger_account import (
    LedgerAccount,
    LedgerAccountType,
    LedgerAccountResourceType,
)
from accounting.models.product import Product, ProductResourceType
from accounting.models.tax_rate import TaxRate, TaxRateResourceType, TaxRateTypes
from accounting.models.project import Project, ProjectResourceType
from accounting.models.contact import Contact, ContactResourceType
from accounting.models.workflow import Workflow, WorkflowResourceType, WorkflowTypes
from moneybird import resources
from moneybird.models import (
    SynchronizableMoneybirdResourceModel,
    MoneybirdDocumentLineModel,
)
from moneybird.resource_types import MoneybirdResource, MoneybirdResourceId


class RecurringSalesInvoiceFrequencies(models.TextChoices):
    DAY = "day", _("day")
    WEEK = "week", _("week")
    MONTH = "month", _("month")
    QUARTER = "quarter", _("quarter")
    YEAR = "year", _("year")


class RecurringSalesInvoice(SynchronizableMoneybirdResourceModel):
    active = models.BooleanField(verbose_name=_("active"), default=True)

    contact = models.ForeignKey(
        Contact,
        null=True,
        blank=False,
        on_delete=models.SET_NULL,
        verbose_name=_("contact"),
        related_name="recurring_sales_invoices",
    )
    workflow = models.ForeignKey(
        Workflow,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={"active": True, "type": WorkflowTypes.INVOICE_WORKFLOW},
        verbose_name=_("workflow"),
    )
    reference = models.CharField(
        max_length=255, null=True, blank=True, verbose_name=_("reference")
    )

    frequency_type = models.CharField(
        max_length=10,
        choices=RecurringSalesInvoiceFrequencies.choices,
        verbose_name=_("frequency type"),
    )
    frequency = models.PositiveSmallIntegerField(verbose_name=_("frequency"))
    first_due_interval = models.PositiveSmallIntegerField(
        null=True, blank=True, verbose_name=_("first due interval")
    )

    auto_send = models.BooleanField(default=True, verbose_name=_("auto send"))

    start_date = models.DateField(null=True, verbose_name=_("start date"))
    invoice_date = models.DateField(
        null=True, blank=True, verbose_name=_("invoice date")
    )
    last_date = models.DateField(null=True, verbose_name=_("last date"))

    discount = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("discount"),
    )
    prices_are_incl_tax = models.BooleanField(
        default=True, verbose_name=_("prices are incl. tax")
    )

    total_price = models.DecimalField(
        max_digits=19, decimal_places=2, verbose_name=_("total price"), null=True
    )

    def __str__(self):
        return f"{_('Recurring sales invoice for')} {self.contact} {_('every')} {self.frequency} {self.frequency_type} {_('since')} {self.start_date}"

    class Meta:
        verbose_name = _("recurring sales invoice")
        verbose_name_plural = _("recurring sales invoices")
        ordering = ("-start_date",)


class RecurringSalesInvoiceDocumentLine(MoneybirdDocumentLineModel):
    description = models.TextField(verbose_name=_("description"), null=True, blank=True)
    total_amount = models.DecimalField(
        max_digits=19,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("total amount"),
    )
    ledger_account = models.ForeignKey(
        LedgerAccount,
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
        verbose_name=_("ledger account"),
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("project"),
    )
    amount = models.CharField(
        verbose_name=_("amount"), null=True, blank=True, default="1 x", max_length=255
    )
    amount_decimal = models.DecimalField(
        null=True,
        max_digits=19,
        decimal_places=2,
        blank=True,
        verbose_name=_("amount (decimal)"),
    )
    price = models.DecimalField(
        max_digits=19, decimal_places=2, verbose_name=_("price")
    )
    document = models.ForeignKey(
        RecurringSalesInvoice,
        on_delete=models.CASCADE,
        verbose_name=_("document"),
        related_name="document_lines",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("product"),
    )
    tax_rate = models.ForeignKey(
        TaxRate,
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
        verbose_name=_("tax rate"),
        limit_choices_to={"active": True, "type": TaxRateTypes.SALES_INVOICE},
    )
    row_order = models.PositiveSmallIntegerField(
        null=True, blank=True, verbose_name=_("row order")
    )

    date = AnnotationProperty(F("document__start_date"))

    @property
    def contact(self):
        return self.document.contact

    def __str__(self):
        return f"{self.amount} {self.description} in {self.document}"

    class Meta:
        verbose_name = _("recurring sales invoice document line")
        verbose_name_plural = _("recurring sales invoice document lines")
        ordering = (
            "-document__start_date",
            "row_order",
        )


class RecurringSalesInvoiceResourceType(resources.RecurringSalesInvoiceResourceType):
    model = RecurringSalesInvoice
    document_lines_model = RecurringSalesInvoiceDocumentLine
    document_lines_foreign_key = "document_lines"
    document_foreign_key = "document"

    @classmethod
    def get_model_kwargs(cls, data):
        kwargs = super().get_model_kwargs(data)
        kwargs["active"] = data["active"]
        kwargs["contact"] = ContactResourceType.get_or_create_from_moneybird_data(
            data["contact_id"]
        )
        kwargs["workflow"] = WorkflowResourceType.get_or_create_from_moneybird_data(
            data["workflow_id"]
        )
        kwargs["reference"] = data["reference"]
        kwargs["frequency_type"] = RecurringSalesInvoiceFrequencies(
            data["frequency_type"]
        )
        kwargs["frequency"] = data["frequency"]
        kwargs["first_due_interval"] = data["first_due_interval"]
        kwargs["auto_send"] = data["auto_send"]
        kwargs["start_date"] = datetime.datetime.fromisoformat(
            data["start_date"]
        ).date()
        kwargs["invoice_date"] = datetime.datetime.fromisoformat(
            data["invoice_date"]
        ).date()
        if data["last_date"]:
            kwargs["last_date"] = datetime.datetime.fromisoformat(
                data["last_date"]
            ).date()
        kwargs["discount"] = data["discount"]
        kwargs["prices_are_incl_tax"] = data["prices_are_incl_tax"]
        kwargs["total_price"] = data["total_price_incl_tax_base"]
        return kwargs

    @classmethod
    def get_document_line_model_kwargs(cls, line_data: MoneybirdResource, document):
        kwargs = super().get_document_line_model_kwargs(line_data, document)
        kwargs["document"] = document
        kwargs["description"] = line_data["description"]
        kwargs[
            "ledger_account"
        ] = LedgerAccountResourceType.get_or_create_from_moneybird_data(
            line_data["ledger_account_id"]
        )
        kwargs["project"] = ProjectResourceType.get_or_create_from_moneybird_data(
            line_data["project_id"]
        )
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
        kwargs["total_amount"] = line_data["total_price_excl_tax_with_discount_base"]
        ledger_account = kwargs["ledger_account"]
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
        data["reference"] = instance.reference or ""
        if instance.discount:
            data["discount"] = float(instance.discount)
        data["prices_are_incl_tax"] = instance.prices_are_incl_tax
        data["first_due_interval"] = instance.first_due_interval
        data["frequency_type"] = instance.frequency_type
        data["frequency"] = instance.frequency
        data["auto_send"] = instance.auto_send
        data["mergeable"] = True
        if instance.invoice_date:
            data["invoice_date"] = instance.invoice_date.isoformat()
        return data

    @classmethod
    def serialize_document_line_for_moneybird(cls, document_line, document):
        data = super().serialize_document_line_for_moneybird(document_line, document)
        data["description"] = document_line.description
        data["ledger_account_id"] = document_line.ledger_account.moneybird_id
        if document_line.project:
            data["project_id"] = document_line.project.moneybird_id
        data["amount"] = document_line.amount
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

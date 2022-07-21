from django.db import models
from django.utils.translation import gettext as _

from accounting.models.contact import Contact, ContactResourceType
from accounting.models.workflow import Workflow, WorkflowResourceType
from moneybird import resources
from moneybird.models import (
    SynchronizableMoneybirdResourceModel,
    MoneybirdDocumentLineModel,
    get_or_create_from_moneybird_data,
)
from moneybird.resource_types import MoneybirdResource, MoneybirdResourceId


class RecurringSalesInvoiceFrequencies(models.TextChoices):
    DAY = "day", _("day")
    WEEK = "week", _("week")
    MONTH = "month", _("month")
    QUARTER = "quarter", _("quarter")
    YEAR = "year", _("year")


class RecurringSalesInvoice(SynchronizableMoneybirdResourceModel):
    moneybird_json = models.JSONField(verbose_name=_("JSON MoneyBird"), null=True)
    contact = models.ForeignKey(
        Contact,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Contact"),
        related_name="recurring_sales_invoices",
    )
    auto_send = models.BooleanField(verbose_name=_("Auto send"))
    active = models.BooleanField(verbose_name=_("Active"))
    frequency = models.CharField(
        max_length=10,
        choices=RecurringSalesInvoiceFrequencies.choices,
        verbose_name=_("frequency"),
    )
    start_date = models.DateField(null=True, verbose_name=_("start date"))
    invoice_date = models.DateField(null=True, verbose_name=_("invoice date"))
    last_date = models.DateField(null=True, verbose_name=_("last date"))
    workflow = models.ForeignKey(
        Workflow, null=True, on_delete=models.SET_NULL, verbose_name=_("Workflow")
    )
    total_price = models.DecimalField(
        max_digits=19, decimal_places=2, verbose_name=_("total price"), null=True
    )

    def __str__(self):
        return f"PER {self.contact} every {self.frequency} since {self.start_date}"

    class Meta:
        verbose_name = _("Recurring sales invoice")
        verbose_name_plural = _("Recurring sales invoices")
        ordering = ("-start_date",)


class RecurringSalesInvoiceDocumentLine(MoneybirdDocumentLineModel):
    moneybird_json = models.JSONField(verbose_name=_("JSON MoneyBird"), null=True)
    document = models.ForeignKey(
        RecurringSalesInvoice,
        on_delete=models.CASCADE,
        verbose_name=_("Document"),
        related_name="document_lines",
    )
    description = models.TextField(
        verbose_name=_("Description"), null=False, blank=False
    )
    asset_id_field = models.CharField(
        max_length=50, null=True, verbose_name=_("Asset Id")
    )
    asset = models.ForeignKey(
        "inventory.Asset",
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Asset"),
        related_name="recurring_sales_invoice_document_lines",
    )

    def __str__(self):
        return f"Line in {self.document} with asset {self.asset_id}"

    class Meta:
        verbose_name = _("Recurring sales invoice document line")
        verbose_name_plural = _("Recurring sales invoice document lines")
        ordering = ("-document__start_date",)


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
        kwargs["contact"] = get_or_create_from_moneybird_data(
            ContactResourceType, data["contact_id"]
        )
        kwargs["workflow"] = get_or_create_from_moneybird_data(
            WorkflowResourceType, data["workflow_id"]
        )
        kwargs["total_price"] = data["total_price_incl_tax_base"]

        return kwargs

    @classmethod
    def get_document_line_model_kwargs(cls, line_data: MoneybirdResource, document):
        kwargs = super().get_document_line_model_kwargs(line_data, document)
        kwargs["document"] = document
        kwargs["moneybird_json"] = line_data
        kwargs["description"] = line_data["description"]
        return kwargs

    @classmethod
    def serialize_for_moneybird(cls, instance):
        data = super().serialize_for_moneybird(instance)
        if instance.contact:
            data["contact"] = MoneybirdResourceId(instance.contact.moneybird_id)
        if instance.workflow:
            data["workflow_id"] = MoneybirdResourceId(instance.workflow.moneybird_id)
        return data

    @classmethod
    def serialize_document_line_for_moneybird(cls, document_line, document):
        data = super().serialize_document_line_for_moneybird(document_line, document)
        data["description"] = document_line.description
        # data["price"] = float(document_line.price)
        return data

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
from moneybird.resource_types import MoneybirdResourceId, MoneybirdResource


class EstimateStateChoices(models.TextChoices):
    DRAFT = "draft", _("draft")
    OPEN = "open", _("open")
    LATE = "late", _("late")
    ACCEPTED = "accepted", _("accepted")
    REJECTED = "rejected", _("rejected")
    BILLED = "billed", _("billed")
    ARCHIVED = "archived", _("archived")


class Estimate(SynchronizableMoneybirdResourceModel):
    moneybird_json = models.JSONField(verbose_name=_("JSON MoneyBird"), null=True)
    date = models.DateField(null=True, verbose_name=_("Date"))
    contact = models.ForeignKey(
        Contact,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Contact"),
        related_name="estimates",
    )
    workflow = models.ForeignKey(
        Workflow, null=True, on_delete=models.SET_NULL, verbose_name=_("Workflow")
    )
    total_price = models.DecimalField(
        max_digits=19, decimal_places=2, verbose_name=_("total price"), null=True
    )
    state = models.CharField(
        max_length=10,
        choices=EstimateStateChoices.choices,
        verbose_name=_("State"),
        default=EstimateStateChoices.DRAFT,
    )

    def __str__(self):
        if self.moneybird_json["estimate_id"] is not None:
            return f"OFF {self.moneybird_json['estimate_id']}"
        return f"OFF {_('draft')} {self.moneybird_json['draft_id']}"

    class Meta:
        verbose_name = _("Estimate")
        verbose_name_plural = _("Estimates")
        ordering = ("-date",)


class EstimateDocumentLine(MoneybirdDocumentLineModel):
    moneybird_json = models.JSONField(verbose_name=_("JSON MoneyBird"), null=True)
    description = models.TextField(
        verbose_name=_("Description"), null=False, blank=False
    )
    document = models.ForeignKey(
        Estimate,
        on_delete=models.CASCADE,
        verbose_name=_("Document"),
        related_name="document_lines",
    )
    asset_id_field = models.CharField(
        max_length=50, null=True, verbose_name=_("Asset Id")
    )
    asset = models.ForeignKey(
        "inventory.Asset",
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Asset"),
        related_name="estimate_document_lines",
    )

    def __str__(self):
        return f"Line in {self.document} with asset {self.asset_id}"

    class Meta:
        verbose_name = _("Estimate document line")
        verbose_name_plural = _("Estimate document lines")
        ordering = ("-document__date",)


class EstimateResourceType(resources.EstimateResourceType):
    model = Estimate
    document_lines_model = EstimateDocumentLine
    document_lines_foreign_key = "document_lines"
    document_foreign_key = "document"

    @classmethod
    def get_model_kwargs(cls, data):
        kwargs = super().get_model_kwargs(data)
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
        data["date"] = instance.date.isoformat()
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
        return data

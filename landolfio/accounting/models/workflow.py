from django.db import models
from django.utils.translation import gettext as _

from moneybird import resources
from moneybird.models import (
    MoneybirdResourceModel,
)


class WorkflowTypes(models.TextChoices):
    INVOICE_WORKFLOW = "InvoiceWorkflow", _("Invoice")
    ESTIMATE_WORKFLOW = "EstimateWorkflow", _("Estimate")


class Workflow(MoneybirdResourceModel):
    name = models.CharField(
        max_length=100,
    )

    type = models.CharField(
        max_length=20,
        choices=WorkflowTypes.choices,
        verbose_name=_("type"),
        default=WorkflowTypes.INVOICE_WORKFLOW,
    )

    active = models.BooleanField(default=True)

    is_rental = models.BooleanField(default=False)
    is_loan = models.BooleanField(default=False)
    is_direct_debit = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("Workflow")
        verbose_name_plural = _("Workflows")

    def __str__(self):
        return self.name


class WorkflowResourceType(resources.WorkflowResourceType):
    model = Workflow

    @classmethod
    def get_model_kwargs(cls, resource_data):
        kwargs = super().get_model_kwargs(resource_data)
        kwargs["name"] = resource_data["name"]
        kwargs["type"] = resource_data["type"]
        kwargs["active"] = resource_data["active"]
        return kwargs

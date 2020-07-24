from django.db import models

from moneybird_accounting.models import MoneybirdReadOnlyResourceModel


class Workflow(MoneybirdReadOnlyResourceModel):
    class Meta:
        verbose_name = "workflow"
        verbose_name_plural = "workflows"

    moneybird_resource_path_name = "workflows"
    moneybird_resource_name = "workflow"

    moneybird_data_fields = [
        "type",
        "name",
        "default",
        "active",
        "prices_are_incl_tax",
    ]

    WORKFLOW_TYPE_INVOICE_WORKFLOW = "InvoiceWorkflow"
    WORKFLOW_TYPE_ESTIMATE_WORKFLOW = "EstimateWorkflow"
    WORKFLOW_TYPES = (
        (WORKFLOW_TYPE_INVOICE_WORKFLOW, "Invoice Workflow"),
        (WORKFLOW_TYPE_ESTIMATE_WORKFLOW, "Estimate Workflow"),
    )

    type = models.CharField(blank=True, null=True, choices=WORKFLOW_TYPES, max_length=20)

    name = models.CharField(blank=True, null=True, max_length=100)

    default = models.BooleanField(blank=True, null=True)
    active = models.BooleanField(blank=True, null=True)
    prices_are_incl_tax = models.BooleanField(blank=True, null=True)

    def __str__(self):
        return self.name

from django.db import models
from django.utils.translation import gettext as _

from moneybird import resources
from moneybird.models import (
    MoneybirdResourceModel,
)


class TaxRateTypes(models.TextChoices):
    SALES_INVOICE = "sales_invoice", _("Sales invoice")
    PURCHASE_INVOICE = "purchase_invoice", _("Purchase invoice")
    GENERAL_JOURNAL_DOCUMENT = "general_journal_document", _("General journal document")


class TaxRate(MoneybirdResourceModel):
    name = models.CharField(
        max_length=100,
    )

    type = models.CharField(
        max_length=24,
        choices=TaxRateTypes.choices,
        verbose_name=_("type"),
        default=TaxRateTypes.SALES_INVOICE,
    )

    active = models.BooleanField(default=True)

    def __str__(self):
        if self.name:
            return f"{self.name} ({self.type})"
        return f"{self.type} tax rate {self.moneybird_id}"

    class Meta:
        verbose_name = _("Tax rate")
        verbose_name_plural = _("Tax rates")


class TaxRateResourceType(resources.TaxRateResourceType):
    model = TaxRate

    @classmethod
    def get_model_kwargs(cls, resource_data):
        kwargs = super().get_model_kwargs(resource_data)
        kwargs["name"] = resource_data["name"]
        kwargs["type"] = resource_data["tax_rate_type"]
        kwargs["active"] = resource_data["active"]
        return kwargs

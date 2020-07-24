from django.db import models

from moneybird_accounting.models import MoneybirdReadOnlyResourceModel


class TaxRate(MoneybirdReadOnlyResourceModel):
    class Meta:
        verbose_name = "tax rate"
        verbose_name_plural = "tax rates"

    moneybird_resource_path_name = "tax_rates"
    moneybird_resource_name = "tax_rate"

    moneybird_data_fields = [
        "name",
        "percentage",
        "show_tax",
        "active",
    ]  # TODO add taxratetype

    name = models.CharField(blank=True, null=True, max_length=100)
    percentage = models.DecimalField(blank=True, null=True, max_digits=5, decimal_places=2)
    show_tax = models.BooleanField(blank=True, null=True)
    active = models.BooleanField(blank=True, null=True)

    def __str__(self):
        return self.name

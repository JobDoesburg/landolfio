from django.db import models
from django.utils.translation import gettext as _

from accounting.models.ledger_account import LedgerAccountResourceType
from accounting.models.tax_rate import TaxRateResourceType, TaxRateTypes
from moneybird import resources
from moneybird.models import (
    MoneybirdResourceModel,
)


class ProductFrequencies(models.TextChoices):
    DAY = "day", _("daily")
    WEEK = "week", _("weekly")
    MONTH = "month", _("monthly")
    QUARTER = "quarter", _("quarterly")
    YEAR = "year", _("yearly")


class Product(MoneybirdResourceModel):
    title = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    description = models.TextField(
        null=True,
        blank=True,
    )
    identifier = models.CharField(
        max_length=100,
        null=True,
        blank=True,
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    frequency = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
    )
    frequency_type = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        choices=ProductFrequencies.choices,
        verbose_name=_("frequency type"),
    )
    tax_rate = models.ForeignKey(
        "TaxRate",
        on_delete=models.PROTECT,
        limit_choices_to={"active": True, "type": TaxRateTypes.SALES_INVOICE},
    )
    ledger_account = models.ForeignKey(
        "LedgerAccount",
        on_delete=models.PROTECT,
    )

    def __str__(self):
        if self.identifier:
            return self.identifier
        if self.title:
            return self.title
        if self.description:
            return self.description
        return self.moneybird_id


class ProductResourceType(resources.ProductResourceType):
    model = Product

    @classmethod
    def get_model_kwargs(cls, resource_data):
        kwargs = super().get_model_kwargs(resource_data)
        kwargs["title"] = resource_data["title"]
        kwargs["description"] = resource_data["description"]
        kwargs["identifier"] = resource_data["identifier"]
        kwargs["price"] = resource_data["price"]
        kwargs["frequency"] = resource_data["frequency"]
        kwargs["frequency_type"] = resource_data["frequency_type"]
        kwargs["tax_rate"] = TaxRateResourceType.get_or_create_from_moneybird_data(
            resource_data["tax_rate_id"]
        )
        kwargs[
            "ledger_account"
        ] = LedgerAccountResourceType.get_or_create_from_moneybird_data(
            resource_data["ledger_account_id"]
        )
        return kwargs

    @classmethod
    def serialize_for_moneybird(cls, instance):
        data = super().serialize_for_moneybird(instance)
        data["title"] = instance.title
        data["description"] = instance.description
        data["identifier"] = instance.identifier
        data["price"] = str(instance.price)
        data["frequency"] = instance.frequency
        data["frequency_type"] = instance.frequency_type
        data["tax_rate_id"] = instance.tax_rate.moneybird_id
        data["ledger_account_id"] = instance.ledger_account.moneybird_id

        if not instance.moneybird_id:
            data["currency"] = "EUR"

        return data

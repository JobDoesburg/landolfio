from django.db import models
from django.utils.translation import gettext as _

from moneybird import resources
from moneybird.models import (
    MoneybirdResourceModel,
)


class LedgerAccountType(models.TextChoices):
    NON_CURRENT_ASSETS = "non_current_assets", _("non current assets")
    CURRENT_ASSETS = "current_assets", _("current assets")
    EQUITY = "equity", _("equity")
    PROVISIONS = "provisions", _("provisions")
    NON_CURRENT_LIABILITIES = "non_current_liabilities", _("non current liabilities")
    CURRENT_LIABILITIES = "current_liabilities", _("current liabilities")
    REVENUE = "revenue", _("revenue")
    DIRECT_COSTS = "direct_costs", _("direct costs")
    EXPENSES = "expenses", _("expenses")
    OTHER_INCOME_EXPENSES = "other_income_expenses", _("other income expenses")


class LedgerAccount(MoneybirdResourceModel):

    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("parent"),
    )

    name = models.CharField(
        max_length=100,
        verbose_name=_("name"),
    )

    account_type = models.CharField(
        max_length=100,
        choices=LedgerAccountType.choices,
        verbose_name=_("account type"),
    )

    is_margin = models.BooleanField(
        default=False,
        verbose_name=_("is margin"),
        help_text=_("All assets on this ledger account are margin assets."),
    )

    is_sales = models.BooleanField(
        default=False,
        verbose_name=_("is sales"),
        help_text=_("Ledger account is used for selling assets."),
    )

    is_purchase = models.BooleanField(
        default=False,
        verbose_name=_("is purchase"),
        help_text=_("Ledger account is used for purchasing assets."),
    )

    class Meta:
        verbose_name = _("ledger account")
        verbose_name_plural = _("ledger accounts")

    def __str__(self):
        return self.name


class LedgerAccountResourceType(resources.LedgerAccountResourceType):
    model = LedgerAccount

    @classmethod
    def get_model_kwargs(cls, data):
        kwargs = super().get_model_kwargs(data)
        kwargs["name"] = data["name"]
        kwargs["account_type"] = data["account_type"]
        kwargs["parent"] = LedgerAccountResourceType.get_or_create_from_moneybird_data(
            data["parent_id"]
        )
        return kwargs

    @classmethod
    def serialize_for_moneybird(cls, instance):
        data = super().serialize_for_moneybird(instance)
        data["name"] = instance.name
        data["account_type"] = instance.account_type
        if instance.parent:
            data["parent_id"] = instance.parent.moneybird_id
        return data

from autocompletefilter.admin import AutocompleteFilterMixin
from autocompletefilter.filters import AutocompleteListFilter
from django.contrib.admin import register

from accounting.models.ledger_account import LedgerAccount
from moneybird.admin import MoneybirdResourceModelAdmin


@register(LedgerAccount)
class LedgerAccountAdmin(AutocompleteFilterMixin, MoneybirdResourceModelAdmin):
    ordering = ("name",)
    list_display = (
        "name",
        "account_type",
        "parent",
        "view_on_moneybird",
        "_synced_with_moneybird",
    )
    list_filter = (
        "account_type",
        "is_margin",
        "is_sales",
        "is_purchase",
        ("parent", AutocompleteListFilter),
    )
    search_fields = (
        "name",
        "account_type",
    )
    has_non_moneybird_fields = True

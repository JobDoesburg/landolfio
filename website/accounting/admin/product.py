from autocompletefilter.admin import AutocompleteFilterMixin
from autocompletefilter.filters import AutocompleteListFilter
from django.contrib.admin import register

from accounting.models.product import Product
from moneybird.admin import MoneybirdResourceModelAdmin


@register(Product)
class ProductAdmin(AutocompleteFilterMixin, MoneybirdResourceModelAdmin):
    ordering = (
        "description",
        "title",
    )
    autocomplete_fields = (
        "tax_rate",
        "ledger_account",
    )

    list_display = (
        "__str__",
        "price",
        "frequency",
        "frequency_type",
        "tax_rate",
        "ledger_account",
        "view_on_moneybird",
    )
    list_filter = (
        ("tax_rate", AutocompleteListFilter),
        ("ledger_account", AutocompleteListFilter),
        "frequency_type",
    )

    search_fields = (
        "title",
        "description",
        "identifier",
    )

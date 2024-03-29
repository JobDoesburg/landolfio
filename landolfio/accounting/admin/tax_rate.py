from django.contrib.admin import register

from accounting.models.tax_rate import TaxRate
from moneybird.admin import MoneybirdResourceModelAdmin


@register(TaxRate)
class TaxRateAdmin(MoneybirdResourceModelAdmin):
    ordering = (
        "-active",
        "name",
    )
    list_display = (
        "name",
        "type",
        "active",
        "view_on_moneybird",
        "_synced_with_moneybird",
    )
    list_filter = (
        "type",
        "active",
    )
    search_fields = (
        "name",
        "type",
    )

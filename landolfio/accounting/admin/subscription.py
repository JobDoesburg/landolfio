from autocompletefilter.admin import AutocompleteFilterMixin
from autocompletefilter.filters import AutocompleteListFilter
from django.contrib.admin import register

from accounting.models import Subscription
from moneybird.admin import MoneybirdResourceModelAdmin


@register(Subscription)
class SubscriptionAdmin(AutocompleteFilterMixin, MoneybirdResourceModelAdmin):
    list_display = (
        "contact",
        "reference",
        "start_date",
        "end_date",
        "cancelled_at",
        "view_on_moneybird",
        "_synced_with_moneybird",
    )
    list_filter = (("contact", AutocompleteListFilter), "end_date", "cancelled_at")
    date_hierarchy = "start_date"

    search_fields = (
        "reference",
        "contact__company_name",
        "contact__first_name",
        "contact__last_name",
        "contact__customer_id",
    )

    autocomplete_fields = ("contact",)

    readonly_fields = (
        "end_date",
        "cancelled_at",
    )

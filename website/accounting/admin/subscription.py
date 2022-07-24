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
        "product",
        "frequency",
        "frequency_type",
        "start_date",
        "end_date",
        "cancelled_at",
    )
    list_filter = (("contact", AutocompleteListFilter), "end_date", "cancelled_at")
    date_hierarchy = "start_date"

    search_fields = (
        "product__title",
        "product__description",
        "reference",
        "contact__company_name",
        "contact__first_name",
        "contact__last_name",
        "contact__customer_id",
    )

    autocomplete_fields = (
        "contact",
        "product",
    )

    readonly_fields = (
        "recurring_sales_invoice",
        "end_date",
        "cancelled_at",
    )

from autocompletefilter.admin import AutocompleteFilterMixin
from autocompletefilter.filters import AutocompleteListFilter
from django.contrib import admin
from django.contrib.admin import register

from accounting.models.estimate import Estimate, EstimateDocumentLine
from moneybird.admin import MoneybirdResourceModelAdmin


class EstimateDocumentLineInline(admin.StackedInline):
    """The admin view for DocumentLines."""

    model = EstimateDocumentLine
    fields = (
        "amount",
        "amount_decimal",
        "description",
        "product",
        "price",
        "ledger_account",
        "tax_rate",
        "project",
        "row_order",
        "total_amount",
        "asset_id_field",
        "asset",
    )
    readonly_fields = ["amount_decimal", "total_amount"]
    extra = 0
    autocomplete_fields = ["product", "ledger_account", "tax_rate", "project", "asset"]
    min_num = 1


@register(Estimate)
class EstimateAdmin(AutocompleteFilterMixin, MoneybirdResourceModelAdmin):
    list_display = (
        "__str__",
        "reference",
        "contact",
        "workflow",
        "total_price",
        "state",
    )
    list_filter = (
        "state",
        ("workflow", AutocompleteListFilter),
        ("contact", AutocompleteListFilter),
    )
    date_hierarchy = "estimate_date"

    search_fields = (
        "estimate_id",
        "reference",
        "draft_id",
        "contact__company_name",
        "contact__first_name",
        "contact__last_name",
        "contact__customer_id",
    )

    readonly_fields = (
        "estimate_id",
        "draft_id",
        "url",
        "public_view_code",
        "sent_at",
        "accepted_at",
        "rejected_at",
        "archived_at",
        "original_estimate",
        "state",
        "total_price",
    )
    autocomplete_fields = (
        "contact",
        "workflow",
    )
    inlines = (EstimateDocumentLineInline,)

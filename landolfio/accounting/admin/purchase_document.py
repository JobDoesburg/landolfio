from autocompletefilter.admin import AutocompleteFilterMixin
from autocompletefilter.filters import AutocompleteListFilter
from django.contrib import admin
from django.contrib.admin import register

from accounting.models import PurchaseDocument, PurchaseDocumentLine
from moneybird.admin import (
    MoneybirdResourceModelAdmin,
    MoneybirdResourceModelAdminMixin,
)


class PurchaseDocumentLineInline(MoneybirdResourceModelAdminMixin, admin.StackedInline):
    model = PurchaseDocumentLine
    fields = (
        "amount",
        "amount_decimal",
        "description",
        "price",
        "ledger_account",
        "tax_rate",
        "project",
        "row_order",
        "total_amount",
    )
    readonly_fields = ["amount_decimal", "total_amount"]
    extra = 0
    autocomplete_fields = ["ledger_account", "tax_rate", "project", "asset"]
    min_num = 1


@register(PurchaseDocument)
class PurchaseDocumentAdmin(AutocompleteFilterMixin, MoneybirdResourceModelAdmin):
    list_display = (
        "__str__",
        "date",
        "contact",
        "total_price",
        "state",
        "view_on_moneybird",
        "_synced_with_moneybird",
    )
    list_filter = (
        "state",
        ("contact", AutocompleteListFilter),
        "document_kind",
    )
    date_hierarchy = "date"

    search_fields = (
        "reference",
        "contact__company_name",
        "contact__first_name",
        "contact__last_name",
        "contact__customer_id",
    )

    readonly_fields = (
        "paid_at",
        "total_price",
        "state",
    )
    autocomplete_fields = ("contact",)
    inlines = (PurchaseDocumentLineInline,)

from autocompletefilter.admin import AutocompleteFilterMixin
from autocompletefilter.filters import AutocompleteListFilter
from django.contrib import admin
from django.contrib.admin import register

from accounting.models import SalesInvoice, PurchaseDocument, PurchaseDocumentLine
from accounting.models.sales_invoice import SalesInvoiceDocumentLine
from moneybird.admin import MoneybirdResourceModelAdmin


class PurchaseDocumentLineInline(admin.StackedInline):
    """The admin view for DocumentLines."""

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
        "asset_id_field",
        "asset",
    )
    readonly_fields = ["amount_decimal", "total_amount"]
    extra = 0
    autocomplete_fields = ["ledger_account", "tax_rate", "project", "asset"]


@register(PurchaseDocument)
class PurchaseDocumentAdmin(AutocompleteFilterMixin, MoneybirdResourceModelAdmin):
    ordering = ("-date", "reference")
    list_display = (
        "__str__",
        "contact",
        "total_price",
        "state",
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

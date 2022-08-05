from autocompletefilter.admin import AutocompleteFilterMixin
from autocompletefilter.filters import AutocompleteListFilter
from django.contrib import admin
from django.contrib.admin import register

from accounting.models import RecurringSalesInvoice, RecurringSalesInvoiceDocumentLine
from moneybird.admin import (
    MoneybirdResourceModelAdmin,
    MoneybirdResourceModelAdminMixin,
)


class RecurringSalesInvoiceDocumentLineInline(
    MoneybirdResourceModelAdminMixin, admin.StackedInline
):
    model = RecurringSalesInvoiceDocumentLine
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
    )
    readonly_fields = ["amount_decimal", "total_amount"]
    extra = 0
    autocomplete_fields = ["product", "ledger_account", "tax_rate", "project", "asset"]
    min_num = 1


@register(RecurringSalesInvoice)
class RecurringSalesInvoiceAdmin(AutocompleteFilterMixin, MoneybirdResourceModelAdmin):
    list_display = (
        "contact",
        "reference",
        "frequency",
        "frequency_type",
        "total_price",
        "start_date",
        "invoice_date",
        "last_date",
        "auto_send",
        "workflow",
        "active",
        "view_on_moneybird",
        "_synced_with_moneybird",
    )
    list_filter = (
        ("workflow", AutocompleteListFilter),
        ("contact", AutocompleteListFilter),
        "active",
        "frequency_type",
        "auto_send",
        "invoice_date",
    )
    date_hierarchy = "start_date"

    search_fields = (
        "reference",
        "contact__company_name",
        "contact__first_name",
        "contact__last_name",
        "contact__customer_id",
    )

    readonly_fields = (
        "total_price",
        "start_date",
        "last_date",
        "active",
    )
    autocomplete_fields = (
        "contact",
        "workflow",
    )
    inlines = (RecurringSalesInvoiceDocumentLineInline,)

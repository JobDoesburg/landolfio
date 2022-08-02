from autocompletefilter.admin import AutocompleteFilterMixin
from autocompletefilter.filters import AutocompleteListFilter
from django.contrib import admin
from django.contrib.admin import register
from django.http import HttpResponseRedirect

from accounting.models import SalesInvoice
from accounting.models.sales_invoice import SalesInvoiceDocumentLine
from moneybird.admin import (
    MoneybirdResourceModelAdmin,
    MoneybirdResourceModelAdminMixin,
)
from website.multi_select_filter import MultiSelectFieldListFilter


class SalesInvoiceDocumentLineInline(
    MoneybirdResourceModelAdminMixin, admin.StackedInline
):
    """The admin view for DocumentLines."""

    model = SalesInvoiceDocumentLine
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


@register(SalesInvoice)
class SalesInvoiceAdmin(AutocompleteFilterMixin, MoneybirdResourceModelAdmin):
    list_display = (
        "__str__",
        "date",
        "reference",
        "contact",
        "workflow",
        "total_price",
        "total_unpaid",
        "state",
        "view_on_moneybird",
        "_synced_with_moneybird",
    )
    list_filter = (
        ("state", MultiSelectFieldListFilter),
        ("workflow", AutocompleteListFilter),
        ("contact", AutocompleteListFilter),
    )
    date_hierarchy = "date"

    search_fields = (
        "invoice_id",
        "reference",
        "draft_id",
        "payment_reference",
        "contact__company_name",
        "contact__first_name",
        "contact__last_name",
        "contact__customer_id",
    )

    readonly_fields = (
        "invoice_id",
        "draft_id",
        "url",
        "payment_url",
        "payment_reference",
        "public_view_code",
        "paid_at",
        "paused",
        "sent_at",
        "total_paid",
        "total_unpaid",
        "total_price",
        "recurring_sales_invoice",
        "original_sales_invoice",
        "state",
    )
    autocomplete_fields = (
        "contact",
        "workflow",
    )
    inlines = (SalesInvoiceDocumentLineInline,)

    def send_invoice(self, request, obj):
        obj.send_invoice()
        self.message_user(request, "This villain is now unique")
        return HttpResponseRedirect(".")

    def get_moneybird_actions(self, request, obj=None):
        actions = super().get_moneybird_actions(request, obj)
        actions.append(
            {
                "label": "Send invoice",
                "func": self.send_invoice,
                "post_parameter": "_moneybird_send_invoice",
            }
        )
        return actions

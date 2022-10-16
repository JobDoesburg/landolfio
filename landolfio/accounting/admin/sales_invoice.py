from autocompletefilter.admin import AutocompleteFilterMixin
from autocompletefilter.filters import AutocompleteListFilter
from django.contrib import admin
from django.contrib.admin import register
from django.http import HttpResponseRedirect
from django.utils.translation import gettext_lazy as _

from accounting.models import SalesInvoice
from accounting.models.sales_invoice import SalesInvoiceDocumentLine
from django_easy_admin_object_actions.admin import ObjectActionsMixin
from django_easy_admin_object_actions.decorators import object_action
from moneybird.admin import (
    MoneybirdResourceModelAdmin,
    MoneybirdResourceModelAdminMixin,
)
from django_admin_multi_select_filter.filters import MultiSelectFieldListFilter


class SalesInvoiceDocumentLineInline(
    MoneybirdResourceModelAdminMixin, admin.StackedInline
):
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
class SalesInvoiceAdmin(
    ObjectActionsMixin, AutocompleteFilterMixin, MoneybirdResourceModelAdmin
):
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

    @object_action(
        label=_("Send invoice"),
        parameter_name="_sendinvoice",
        extra_classes="default",
        condition=lambda request, obj: obj.state == "draft",
        display_as_disabled_if_condition_not_met=True,
        log_message="Invoice sent",
        perform_after_saving=True,
    )
    def send_invoice(self, request, obj):
        # obj.send_invoice()
        # TODO implement this
        # return HttpResponseRedirect(".")
        pass

    @object_action(
        label=_("Resend invoice"),
        parameter_name="_resendinvoice",
        condition=lambda request, obj: obj.state != "draft",
        display_as_disabled_if_condition_not_met=True,
        log_message="Invoice resent",
        perform_after_saving=True,
    )
    def resend_invoice(self, request, obj):
        # obj.send_invoice()
        # TODO implement this
        # return HttpResponseRedirect(".")
        pass

    @object_action(
        label=_("View on moneybird"),
        parameter_name="_viewonmoneybird",
    )
    def view_on_moneybird_action(self, request, obj):
        return HttpResponseRedirect(obj.moneybird_url)

    object_actions_before_fieldsets = (
        "send_invoice",
        "resend_invoice",
        "view_on_moneybird_action",
    )

from django.contrib import admin, messages
from django.db.models.functions import Concat
from django.http import HttpResponseRedirect
from django.utils.html import format_html
from import_export.admin import ImportExportModelAdmin

from moneybird_accounting.models.contact import Contact
from moneybird_accounting.models.sales_invoice import SalesInvoice
from moneybird_accounting.moneybird_sync import MoneyBirdAPITalker, MoneyBirdSynchronizationError


class SalesInvoiceInline(admin.TabularInline):
    model = SalesInvoice
    fields = [
        "invoice_id",
        "invoice_date",
        "state",
        "total_price_incl_tax",
        "total_paid",
        "total_unpaid",
    ]

    readonly_fields = [
        "invoice_id",
        "invoice_date",
        "state",
        "total_price_incl_tax",
        "total_paid",
        "total_unpaid",
    ]
    extra = 0


@admin.register(Contact)
class MoneybirdContactAdmin(ImportExportModelAdmin):
    class Media:
        """Necessary to use AutocompleteFilter."""

    list_display = [
        "get_display_name",
        "firstname",
        "lastname",
        "company_name",
        "email",
        "city",
        "customer_id",
        "sepa_active",
        "get_moneybird_resource_url_short",
    ]
    list_display_links = [
        "get_display_name",
    ]
    search_fields = [
        "company_name",
        "firstname",
        "lastname",
        "email",
        "phone",
        "attention",
    ]
    list_filter = [
        "sepa_active",
    ]

    actions = ["sync_moneybird"]

    view_on_site = True

    fieldsets = [
        ("Name", {"fields": ["company_name", "firstname", "lastname", "attention"]}),
        ("Address", {"fields": ["address1", "address2", "zipcode", "city", "country"],},),
        (
            "Contact",
            {
                "fields": [
                    "phone",
                    "send_invoices_to_email",
                    "send_invoices_to_attention",
                    "send_estimates_to_email",
                    "send_estimates_to_attention",
                    "email",
                    "email_ubl",
                    "delivery_method",
                ],
            },
        ),
        ("Detail", {"fields": ["customer_id", "chamber_of_commerce", "tax_number", "bank_account",],},),
        (
            "SEPA mandate",
            {
                "fields": [
                    "sepa_active",
                    "sepa_iban",
                    "sepa_iban_account_name",
                    "sepa_bic",
                    "sepa_mandate_id",
                    "sepa_sequence_type",
                ],
            },
        ),
        ("Meta", {"fields": ["id", "version", "get_moneybird_resource_url"]}),
    ]

    readonly_fields = ["id", "version", "get_moneybird_resource_url", "email", "attention"]

    inlines = [SalesInvoiceInline]

    def changeform_view(self, request, *args, **kwargs):
        try:
            return super().changeform_view(request, *args, **kwargs)
        except MoneyBirdSynchronizationError as err:
            self.message_user(request, "Moneybird does not accept this data: " + str(err), level=messages.ERROR)
            return HttpResponseRedirect(request.path)

    def get_display_name(self, obj):
        return obj.get_display_name()

    get_display_name.short_description = "Name"
    get_display_name.admin_order_field = Concat("company_name", "firstname", "lastname")

    def get_moneybird_resource_url(self, obj):
        return (
            format_html(f"<a href='{obj.moneybird_resource_url}' target='_blank'>{obj.moneybird_resource_url}</a>")
            if obj.moneybird_resource_url
            else "-"
        )

    get_moneybird_resource_url.short_description = "Moneybird resource URL"

    def get_moneybird_resource_url_short(self, obj):
        return (
            format_html(f"<a href='{obj.moneybird_resource_url}' target='_blank'>View in Moneybird</a>")
            if obj.moneybird_resource_url
            else "-"
        )

    get_moneybird_resource_url_short.short_description = "Moneybird"

    def sync_moneybird(self, *args, **kwargs):
        m = MoneyBirdAPITalker()
        m.sync_objects(self.model)

    sync_moneybird.short_description = "Synchronize with Moneybird"

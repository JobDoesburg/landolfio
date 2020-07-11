from django.contrib import admin, messages
from django.db.models.functions import Concat
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.html import format_html
from import_export.admin import ImportExportModelAdmin

from moneybird_accounting.models import Contact, SalesInvoice, InvoiceDetailItem
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


class InvoiceDetailItemInline(admin.TabularInline):
    model = InvoiceDetailItem
    fields = [
        "amount",
        "amount_decimal",
        "description",
        "price",
        "total_price_excl_tax_with_discount",
        "total_price_excl_tax_with_discount_base",
        "tax_rate_id",
        "ledger_account_id",
        "project_id",
        "product_id",
    ]
    ordering = ["row_order", "id"]

    readonly_fields = [
        "total_price_excl_tax_with_discount",
        "total_price_excl_tax_with_discount_base",
    ]
    extra = 0


@admin.register(SalesInvoice)
class MoneybirdSalesInvoiceAdmin(ImportExportModelAdmin):
    class Media:
        """Necessary to use AutocompleteFilter."""

    list_display = [
        "get_invoice_id",
        "get_contact",
        "invoice_date",
        "reference",
        "state",
        "number_of_rows",
        "total_price_incl_tax",
        "total_paid",
        "total_unpaid",
        "get_moneybird_resource_url_short",
    ]
    list_filter = [
        "state",
    ]
    search_fields = ["invoice_id", "get_invoice_id", "contact", "reference"]

    actions = ["sync_moneybird"]  # TODO Get a nicer and more uniform solution for this

    view_on_site = True

    fieldsets = [
        ("Invoice data", {"fields": ["get_invoice_id", "state", "invoice_date", "due_date"]}),
        ("Details", {"fields": ["reference", "payment_conditions",]}),
        ("Invoice", {"fields": ["discount", "prices_are_incl_tax"]}),
        (
            "Totals",
            {
                "fields": [
                    "total_paid",
                    "total_unpaid",
                    "total_unpaid_base",
                    "total_price_excl_tax",
                    "total_price_excl_tax_base",
                    "total_price_incl_tax",
                    "total_price_incl_tax_base",
                    "total_discount",
                ]
            },
        ),
        ("Extra", {"fields": ["payment_reference", "get_url", "public_view_code", "get_payment_url"]}),
        ("History", {"fields": ["get_original_sales_invoice", "paused", "sent_at", "paid_at"]}),
        ("Meta", {"fields": ["id", "version", "get_moneybird_resource_url"]}),
    ]

    readonly_fields = [
        "get_invoice_id",
        "id",
        "version",
        "invoice_id",
        "draft_id",
        "state",
        "paused",
        "paid_at",
        "sent_at",
        "payment_reference",
        "public_view_code",
        "get_original_sales_invoice",
        "get_url",
        "get_payment_url",
        "total_paid",
        "total_unpaid",
        "total_unpaid_base",
        "total_price_excl_tax",
        "total_price_excl_tax_base",
        "total_price_incl_tax",
        "total_price_incl_tax_base",
        "total_discount",
        "get_moneybird_resource_url",
    ]

    inlines = [InvoiceDetailItemInline]
    # TODO fix this admin layout

    # TODO Create MoneybirdResourceAdmin?

    # TODO refactor admins in multiple files

    def sync_moneybird(self, *args, **kwargs):
        m = MoneyBirdAPITalker()
        m.sync_objects(self.model)

    sync_moneybird.short_description = "Synchronize with Moneybird"

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

    def get_url(self, obj):
        return format_html(f"<a href='{obj.url}' target='_blank'>Customer view in Moneybird</a>") if obj.url else "-"

    get_url.short_description = "Url"

    def get_payment_url(self, obj):
        return (
            format_html(f"<a href='{obj.payment_url}' target='_blank'>Payment view in Moneybird</a>")
            if obj.payment_url
            else "-"
        )

    get_payment_url.short_description = "Payment url"

    def get_original_sales_invoice(self, obj):
        change_url = reverse("admin:moneybird_salesinvoice_change", args=(obj.original_sales_invoice.id,))
        return format_html(f'<a href="{change_url}">{obj.original_sales_invoice}</a>')

    get_original_sales_invoice.short_description = "Invoice based on"

    def get_contact(self, obj):
        change_url = reverse("admin:moneybird_contact_change", args=(obj.contact.id,))
        return format_html(f'<a href="{change_url}">{obj.contact.get_display_name()}</a>')

    get_contact.short_description = "Contact"

    def get_invoice_id(self, obj):
        return str(obj)

    get_invoice_id.short_description = "invoice id"
    get_invoice_id.admin_order_field = Concat("invoice_id", "draft_id")

    def changeform_view(self, request, *args, **kwargs):
        obj_id = args[0]
        if SalesInvoice.objects.get(id=obj_id).state != SalesInvoice.STATE_DRAFT:
            self.message_user(
                request,
                "This invoice is has already been sent. Customers will not be notified about changes you make here.",
                level=messages.WARNING,
            )
        return super().changeform_view(request, *args, **kwargs)

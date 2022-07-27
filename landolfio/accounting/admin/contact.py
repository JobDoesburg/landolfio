from django.contrib import admin
from django.contrib.admin import register
from django.utils.safestring import mark_safe

from accounting.models.contact import Contact
from moneybird.admin import MoneybirdResourceModelAdmin


@register(Contact)
class ContactAdmin(MoneybirdResourceModelAdmin):
    ordering = ("last_name", "first_name", "company_name", "customer_id")
    list_display = (
        "__str__",
        "_email",
        "phone",
        "address_1",
        "city",
        "sepa_active",
        "view_on_moneybird",
        "_synced_with_moneybird",
    )
    list_filter = ("sepa_active",)

    search_fields = (
        "company_name",
        "first_name",
        "last_name",
        "customer_id",
        "email",
        "address_1",
        "address_2",
        "zip_code",
        "city",
        "country",
        "phone",
        "email",
        "tax_number",
        "chamber_of_commerce",
        "attention",
        "send_invoices_to_attention",
        "send_invoices_to_email",
        "send_estimates_to_attention",
        "send_estimates_to_email",
        "sepa_iban",
        "sepa_iban_account_name",
        "sepa_mandate_id",
    )

    readonly_fields = (
        "tax_number_valid",
        "sales_invoices_url",
        "email",
        "attention",
    )
    autocomplete_fields = (
        "invoice_workflow",
        "estimate_workflow",
    )

    @staticmethod
    def _email(instance):
        return mark_safe(f"<a href='mailto:{instance.email}'>{instance.email}</a>")

    @staticmethod
    def _sales_invoice_url(instance):
        return mark_safe(
            f"<a href='{instance.sales_invoices_url}' target='_blank'>{instance.sales_invoices_url}</a>"
        )

"""Accounting admin configuration."""
from django.contrib import admin
from django.contrib.admin import register
from django.utils.safestring import mark_safe
from json2html import json2html

from .models import JournalDocument, Contact
from .models import DocumentLine
from .models import Ledger


@register(Ledger)
class LedgerAdmin(admin.ModelAdmin):
    """The Django admin config for the Ledger model."""

    model = Ledger
    list_display = ("name", "moneybird_id", "account_type", "ledger_kind")
    list_filter = ("account_type",)

    def has_add_permission(self, request):
        """Prevent all users from adding Documents."""
        return False


class DocumentLineAdmin(admin.StackedInline):
    """The admin view for DocumentLines."""

    model = DocumentLine
    fields = ("asset_id_field", "asset", "ledger", "price", "json_mb_html")
    readonly_fields = ["json_mb_html"]
    change_form_template = "admin/accounting/document/change_form.html"
    extra = 0

    def has_add_permission(self, request, obj):
        return False

    def json_mb_html(self, obj):  # pylint: disable = no-self-use
        """Convert JSON to HTML table."""
        return mark_safe(json2html.convert(obj.moneybird_json))

    json_mb_html.short_description = "JSON MoneyBird"


@register(JournalDocument)
class JournalDocumentAdmin(admin.ModelAdmin):
    """The admin view for Documents."""

    model = JournalDocument
    inlines = (DocumentLineAdmin,)

    list_display = ("__str__", "document_kind", "date", "contact", "moneybird_id")
    list_filter = ("document_kind",)

    date_hierarchy = "date"

    readonly_fields = ["json_mb_html"]
    change_form_template = "admin/accounting/document/change_form.html"

    def json_mb_html(self, obj):  # pylint: disable = no-self-use
        """Convert JSON to HTML table."""
        return mark_safe(json2html.convert(obj.moneybird_json))

    json_mb_html.short_description = "JSON MoneyBird"

    def has_add_permission(self, request):
        """Prevent all users from adding Documents."""
        return False


@register(Contact)
class ContactAdmin(admin.ModelAdmin):
    """The admin view for Contacts."""

    model = Contact

    list_display = (
        "__str__",
        "company_name",
        "first_name",
        "last_name",
        "email",
        "sepa_active",
    )
    list_filter = ("sepa_active",)

    def has_add_permission(self, request):
        """Prevent all users from adding Documents."""
        return False

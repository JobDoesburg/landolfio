"""Accounting admin configuration."""
from django.contrib import admin
from django.utils.safestring import mark_safe
from json2html import json2html

from .models import Document
from .models import DocumentLine
from .models import Ledger


class LedgerAdmin(admin.ModelAdmin):
    """The Django admin config for the Ledger model."""

    model = Ledger
    list_display = ("kind", "moneybird_id")


class DocumentLineAdmin(admin.StackedInline):
    """The admin view for DocumentLines."""

    model = DocumentLine
    fields = ("asset_id_field", "asset", "ledger", "json_mb_html")
    readonly_fields = ["json_mb_html"]
    change_form_template = "admin/accounting/document/change_form.html"

    def json_mb_html(self, obj):  # pylint: disable = no-self-use
        """Convert JSON to HTML table."""
        return mark_safe(json2html.convert(obj.moneybird_json))

    json_mb_html.short_description = "JSON MoneyBird"


class DocumentAdmin(admin.ModelAdmin):
    """The admin view for Documents."""

    model = Document
    inlines = (DocumentLineAdmin,)
    readonly_fields = ["json_mb_html"]
    change_form_template = "admin/accounting/document/change_form.html"

    def json_mb_html(self, obj):  # pylint: disable = no-self-use
        """Convert JSON to HTML table."""
        return mark_safe(json2html.convert(obj.moneybird_json))

    json_mb_html.short_description = "JSON MoneyBird"

    def has_add_permission(self, request):
        """Prevent all users from adding Documents."""
        return False

    def has_change_permission(self, request, obj=None):
        """Prevent all users from changing Documents."""
        return False


admin.site.register(Ledger, LedgerAdmin)
admin.site.register(Document, DocumentAdmin)

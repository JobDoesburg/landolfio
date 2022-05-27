"""Accounting admin configuration."""
from django.contrib import admin
from django.utils.safestring import mark_safe
from json2html import json2html

from .models import Document
from .models import DocumentLine


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    """
    The admin class for the Document model.
    """

    model = Document
    fields = ["id_MB", "json_mb_html", "kind"]
    readonly_fields = ["json_mb_html"]

    def json_mb_html(self, obj):  # pylint: disable = no-self-use
        """Convert JSON to HTML table."""
        return mark_safe(json2html.convert(obj.json_MB))

    json_mb_html.short_description = "JSON MoneyBird"


@admin.register(DocumentLine)
class DocumentLineAdmin(admin.ModelAdmin):
    """
    The admin class for the DocumentLine model.
    """

    model = DocumentLine
    fields = ["json_mb_html", "ledger", "document", "asset_id_field", "asset"]
    readonly_fields = ["json_mb_html"]

    def json_mb_html(self, obj):  # pylint: disable = no-self-use
        """Convert JSON to HTML table."""
        return mark_safe(json2html.convert(obj.json_MB))

    json_mb_html.short_description = "JSON MoneyBird"

"""Accounting admin configuration."""
from django.contrib import admin
from django.contrib.admin import register
from django.utils.safestring import mark_safe
from json2html import json2html

from accounting.models.contact import Contact
from accounting.models.document_style import DocumentStyle
from accounting.models.estimate import EstimateDocumentLine, Estimate
from accounting.models.journal_document import JournalDocumentLine, JournalDocument
from accounting.models.recurring_sales_invoice import (
    RecurringSalesInvoiceDocumentLine,
    RecurringSalesInvoice,
)
from accounting.models.subscription import Subscription


class JournalDocumentLineInline(admin.StackedInline):
    """The admin view for DocumentLines."""

    model = JournalDocumentLine
    fields = (
        "asset_id_field",
        "asset",
        "description",
        "amount",
        "ledger",
        "price",
        "tax_rate",
        "project",
        "json_mb_html",
    )
    readonly_fields = ["json_mb_html"]
    change_form_template = "admin/accounting/document/change_form.html"
    extra = 0

    def json_mb_html(self, obj):  # pylint: disable = no-self-use
        """Convert JSON to HTML table."""
        return mark_safe(json2html.convert(obj.moneybird_json))

    json_mb_html.short_description = "JSON MoneyBird"


@register(JournalDocument)
class JournalDocumentAdmin(admin.ModelAdmin):
    """The admin view for Documents."""

    inlines = (JournalDocumentLineInline,)

    list_display = (
        "__str__",
        "document_kind",
        "date",
        "contact",
        "total_price",
        "total_paid",
        "total_unpaid",
        "moneybird_id",
    )
    list_filter = (
        "document_kind",
        "workflow",
    )
    search_fields = ["moneybird_json"]
    date_hierarchy = "date"

    readonly_fields = ["json_mb_html"]
    change_form_template = "admin/accounting/document/change_form.html"

    def json_mb_html(self, obj):  # pylint: disable = no-self-use
        """Convert JSON to HTML table."""
        return mark_safe(json2html.convert(obj.moneybird_json))

    json_mb_html.short_description = "JSON MoneyBird"


class EstimateDocumentLineInline(admin.StackedInline):
    """The admin view for DocumentLines."""

    model = EstimateDocumentLine
    fields = ("asset_id_field", "asset", "json_mb_html")
    readonly_fields = ["json_mb_html"]
    change_form_template = "admin/accounting/document/change_form.html"
    extra = 0

    def json_mb_html(self, obj):  # pylint: disable = no-self-use
        """Convert JSON to HTML table."""
        return mark_safe(json2html.convert(obj.moneybird_json))

    json_mb_html.short_description = "JSON MoneyBird"


@register(Estimate)
class EstimateAdmin(admin.ModelAdmin):
    """The admin view for Documents."""

    inlines = (EstimateDocumentLineInline,)

    list_display = ("__str__", "date", "contact", "total_price", "moneybird_id")
    list_filter = ("workflow",)

    date_hierarchy = "date"

    readonly_fields = ["json_mb_html"]
    change_form_template = "admin/accounting/document/change_form.html"

    def json_mb_html(self, obj):  # pylint: disable = no-self-use
        """Convert JSON to HTML table."""
        return mark_safe(json2html.convert(obj.moneybird_json))

    json_mb_html.short_description = "JSON MoneyBird"


class RecurringSalesInvoiceDocumentLineInline(admin.StackedInline):
    """The admin view for DocumentLines."""

    model = RecurringSalesInvoiceDocumentLine
    fields = ("asset_id_field", "asset", "json_mb_html")
    readonly_fields = ["json_mb_html"]
    change_form_template = "admin/accounting/document/change_form.html"
    extra = 0

    def json_mb_html(self, obj):  # pylint: disable = no-self-use
        """Convert JSON to HTML table."""
        return mark_safe(json2html.convert(obj.moneybird_json))

    json_mb_html.short_description = "JSON MoneyBird"


@register(RecurringSalesInvoice)
class RecurringSalesInvoiceAdmin(admin.ModelAdmin):
    """The admin view for Documents."""

    inlines = (RecurringSalesInvoiceDocumentLineInline,)

    list_display = (
        "__str__",
        "start_date",
        "contact",
        "active",
        "frequency",
        "total_price",
        "moneybird_id",
    )
    list_filter = (
        "active",
        "frequency",
        "workflow",
    )

    date_hierarchy = "start_date"

    readonly_fields = ["json_mb_html"]
    change_form_template = "admin/accounting/document/change_form.html"

    def json_mb_html(self, obj):  # pylint: disable = no-self-use
        """Convert JSON to HTML table."""
        return mark_safe(json2html.convert(obj.moneybird_json))

    json_mb_html.short_description = "JSON MoneyBird"


@register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    pass


@register(DocumentStyle)
class DocumentStyleAdmin(admin.ModelAdmin):

    fields = ["json_mb_html"]
    readonly_fields = ["json_mb_html"]

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def json_mb_html(self, obj):  # pylint: disable = no-self-use
        """Convert JSON to HTML table."""
        return mark_safe(json2html.convert(obj.moneybird_json))

    json_mb_html.short_description = "JSON MoneyBird"

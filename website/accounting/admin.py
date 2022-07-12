"""Accounting admin configuration."""
from django.contrib import admin
from django.contrib.admin import register
from django.utils.safestring import mark_safe
from json2html import json2html

from .models import (
    JournalDocument,
    JournalDocumentLine,
    Ledger,
    Contact,
    Estimate,
    EstimateDocumentLine,
    RecurringSalesInvoice,
    RecurringSalesInvoiceDocumentLine,
    Workflow,
    Product,
    TaxRate,
    Project,
)


@register(Ledger)
class LedgerAdmin(admin.ModelAdmin):
    """The Django admin config for the Ledger model."""

    model = Ledger
    list_display = ("name", "moneybird_id", "account_type", "ledger_kind")
    list_filter = ("account_type",)

    search_fields = (
        "name",
        "ledger_kind",
        "moneybird_id",
    )

    def has_add_permission(self, request):
        """Prevent all users from adding Documents."""
        return False


@register(Workflow)
class WorkflowAdmin(admin.ModelAdmin):
    """The Django admin config for the Ledger model."""

    model = Workflow
    list_display = (
        "name",
        "moneybird_id",
    )

    def has_add_permission(self, request):
        """Prevent all users from adding Documents."""
        return False


@register(Product)
class ProductAdmin(admin.ModelAdmin):
    """The Django admin config for the Product model."""

    model = Product
    list_display = (
        "__str__",
        "moneybird_id",
    )


@register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """The Django admin config for the Project model."""

    model = Project
    list_display = (
        "__str__",
        "moneybird_id",
    )


@register(TaxRate)
class TaxRateAdmin(admin.ModelAdmin):
    """The Django admin config for the TaxRate model."""

    model = TaxRate
    list_display = (
        "__str__",
        "moneybird_id",
    )

    def has_add_permission(self, request):
        """Prevent all users from adding Documents."""
        return False


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

    model = JournalDocument
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

    date_hierarchy = "date"

    readonly_fields = ["json_mb_html"]
    change_form_template = "admin/accounting/document/change_form.html"

    def json_mb_html(self, obj):  # pylint: disable = no-self-use
        """Convert JSON to HTML table."""
        return mark_safe(json2html.convert(obj.moneybird_json))

    json_mb_html.short_description = "JSON MoneyBird"


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

    model = Estimate
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

    model = RecurringSalesInvoice
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

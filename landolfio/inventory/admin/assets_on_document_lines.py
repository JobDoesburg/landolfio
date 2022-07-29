from autocompletefilter.admin import AutocompleteFilterMixin
from autocompletefilter.filters import AutocompleteListFilter
from django.contrib import admin
from queryable_properties.admin import QueryablePropertiesAdmin

from accounting.models.journal_document import JournalDocumentLine
from accounting.models.estimate import EstimateDocumentLine
from accounting.models.recurring_sales_invoice import RecurringSalesInvoiceDocumentLine
from inventory.models.asset import (
    AssetOnJournalDocumentLine,
    AssetOnEstimateDocumentLine,
    AssetOnRecurringSalesInvoiceDocumentLine,
)
from moneybird.admin import MoneybirdResourceModelAdmin


class AssetOnJournalDocumentLineInline(admin.TabularInline):
    model = AssetOnJournalDocumentLine
    extra = 0
    autocomplete_fields = ["asset"]


@admin.register(JournalDocumentLine)
class JournalDocumentLineAdmin(
    AutocompleteFilterMixin, QueryablePropertiesAdmin, MoneybirdResourceModelAdmin
):
    list_display = (
        "description",
        "document",
        "date",
        "assets",
        "total_amount",
        "ledger_account",
    )
    list_display_links = ["description", "document", "date"]
    search_fields = ["description", "assets__id"]
    readonly_fields = ["assets"]
    inlines = [AssetOnJournalDocumentLineInline]
    list_filter = [
        ("assets__asset", AutocompleteListFilter),
        ("assets__asset__category", AutocompleteListFilter),
        ("ledger_account", AutocompleteListFilter),
        "ledger_account__account_type",
    ]

    def get_queryset(self, request):
        return super().get_queryset(request).select_subclasses()

    @admin.display
    def assets(self, obj):
        return ", ".join(obj.assets.values_list("asset", flat=True))

    def has_add_permission(self, request, obj=None):
        return False


class AssetOnEstimateDocumentLineInline(admin.TabularInline):
    model = AssetOnEstimateDocumentLine
    extra = 0
    autocomplete_fields = ["asset"]


@admin.register(EstimateDocumentLine)
class EstimateDocumentLineAdmin(
    AutocompleteFilterMixin, QueryablePropertiesAdmin, MoneybirdResourceModelAdmin
):
    list_display = (
        "description",
        "document",
        "date",
        "assets",
        "total_amount",
        "ledger_account",
    )
    list_display_links = ["description", "document", "date"]
    search_fields = ["description", "assets__id"]
    readonly_fields = ["assets"]
    inlines = [AssetOnEstimateDocumentLineInline]
    list_filter = [
        ("assets__asset", AutocompleteListFilter),
        ("assets__asset__category", AutocompleteListFilter),
        ("document__workflow", AutocompleteListFilter),
    ]

    @admin.display
    def assets(self, obj):
        return ", ".join(obj.assets.values_list("asset", flat=True))

    def has_add_permission(self, request, obj=None):
        return False


class AssetOnRecurringSalesInvoiceDocumentLineInline(admin.TabularInline):
    model = AssetOnRecurringSalesInvoiceDocumentLine
    extra = 0
    autocomplete_fields = ["asset"]


@admin.register(RecurringSalesInvoiceDocumentLine)
class RecurringSalesInvoiceDocumentLineAdmin(
    AutocompleteFilterMixin, QueryablePropertiesAdmin, MoneybirdResourceModelAdmin
):
    list_display = (
        "description",
        "document",
        "date",
        "assets",
        "total_amount",
        "ledger_account",
    )
    list_display_links = ["description", "document", "date"]
    search_fields = ["description", "assets__id"]
    readonly_fields = ["assets"]
    inlines = [AssetOnRecurringSalesInvoiceDocumentLineInline]
    list_filter = [
        ("assets__asset", AutocompleteListFilter),
        ("assets__asset__category", AutocompleteListFilter),
        ("document__workflow", AutocompleteListFilter),
        ("ledger_account", AutocompleteListFilter),
        "ledger_account__account_type",
    ]

    @admin.display
    def assets(self, obj):
        return ", ".join(obj.assets.values_list("asset", flat=True))

    def has_add_permission(self, request, obj=None):
        return False

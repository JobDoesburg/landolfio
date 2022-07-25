from autocompletefilter.admin import AutocompleteFilterMixin
from autocompletefilter.filters import AutocompleteListFilter
from django.contrib import admin
from model_utils.managers import InheritanceManager

from accounting.models.journal_document import JournalDocumentLine
from accounting.models.estimate import EstimateDocumentLine
from accounting.models.recurring_sales_invoice import RecurringSalesInvoiceDocumentLine
from inventory.models.asset import (
    AssetOnJournalDocumentLine,
    AssetOnEstimateDocumentLine,
    AssetOnRecurringSalesInvoiceDocumentLine,
)
from moneybird.admin import MoneybirdResourceModelAdmin
from model_utils.managers import InheritanceManager


class AssetOnJournalDocumentLineInline(admin.TabularInline):
    model = AssetOnJournalDocumentLine
    extra = 0
    autocomplete_fields = ["asset"]


@admin.register(JournalDocumentLine)
class JournalDocumentLineAdmin(AutocompleteFilterMixin, MoneybirdResourceModelAdmin):
    list_display = (
        "description",
        "total_amount",
        "assets",
    )
    readonly_fields = ["assets"]
    inlines = [AssetOnJournalDocumentLineInline]
    list_filter = [
        ("ledger_account", AutocompleteListFilter),
        ("asset__category", AutocompleteListFilter),
    ]

    def get_queryset(self, request):
        manager = InheritanceManager()
        manager.model = JournalDocumentLine
        qs = manager.get_queryset()
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        if not self.has_view_or_change_permission(request):
            qs = qs.none()
        return qs.select_subclasses()

    @admin.display
    def assets(self, obj):
        return ", ".join(obj.assets.values_list("asset", flat=True))

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False


class AssetOnEstimateDocumentLineInline(admin.TabularInline):
    model = AssetOnEstimateDocumentLine
    extra = 0
    autocomplete_fields = ["asset"]


@admin.register(EstimateDocumentLine)
class EstimateDocumentLineAdmin(AutocompleteFilterMixin, MoneybirdResourceModelAdmin):
    list_display = (
        "description",
        "total_amount",
        "assets",
    )
    readonly_fields = ["assets"]
    inlines = [AssetOnEstimateDocumentLineInline]
    list_filter = [
        ("ledger_account", AutocompleteListFilter),
        ("asset__category", AutocompleteListFilter),
    ]

    @admin.display
    def assets(self, obj):
        return ", ".join(obj.assets.values_list("asset", flat=True))

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False


class AssetOnRecurringSalesInvoiceDocumentLineInline(admin.TabularInline):
    model = AssetOnRecurringSalesInvoiceDocumentLine
    extra = 0
    autocomplete_fields = ["asset"]


@admin.register(RecurringSalesInvoiceDocumentLine)
class RecurringSalesInvoiceDocumentLineAdmin(
    AutocompleteFilterMixin, MoneybirdResourceModelAdmin
):
    list_display = (
        "description",
        "total_amount",
        "assets",
    )
    readonly_fields = ["assets"]
    inlines = [AssetOnRecurringSalesInvoiceDocumentLineInline]
    list_filter = [
        ("ledger_account", AutocompleteListFilter),
        ("asset__category", AutocompleteListFilter),
    ]

    @admin.display
    def assets(self, obj):
        return ", ".join(obj.assets.values_list("asset", flat=True))

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False

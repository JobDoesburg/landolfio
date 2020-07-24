from django.contrib import admin
from django.forms import CheckboxSelectMultiple
from polymorphic.admin import StackedPolymorphicInline, PolymorphicInlineSupportMixin

from asset_events.models import *
from assets.models import *
from maintenance.admin.inlines import (
    AssetReviewEventInline,
    AssetMaintenanceTicketEventInline,
    AssetMaintenanceReturnEventInline,
    AssetAmortizationEventInline,
)
from purchases.admin.inlines import AssetPurchaseEventInline, AssetDeliveryEventInline
from sales.admin.inlines import AssetSaleEventInline
from rentals.admin.inlines import (
    AssetLoanEventInline,
    AssetRentalEventInline,
    AssetReturnalEventInline,
    UnprocessedAssetIssuanceEventInline,
)


class AssetEventHistoryInline(StackedPolymorphicInline):

    model = Event

    child_inlines = [
        AssetPurchaseEventInline,
        AssetDeliveryEventInline,
        AssetSaleEventInline,
        AssetReviewEventInline,
        AssetMaintenanceTicketEventInline,
        AssetMaintenanceReturnEventInline,
        AssetAmortizationEventInline,
        AssetLoanEventInline,
        AssetRentalEventInline,
        AssetReturnalEventInline,
        UnprocessedAssetIssuanceEventInline,
    ]

    extra = 0
    can_delete = False


@admin.register(Asset)
class AssetAdmin(PolymorphicInlineSupportMixin, admin.ModelAdmin):

    list_display = ["number", "category", "size", "status"]
    list_filter = ["category", "status", "size", "location", "location__location_group"]

    readonly_fields = ["status"]

    search_fields = ["number", "event__memo"]

    inlines = [AssetEventHistoryInline]

    class Media:
        """Necessary to use AutocompleteFilter."""


@admin.register(AssetCategory)
class AssetTypeAdmin(admin.ModelAdmin):
    class Media:
        """Necessary to use AutocompleteFilter."""


@admin.register(AssetSize)
class AssetSizeAdmin(admin.ModelAdmin):
    class Media:
        """Necessary to use AutocompleteFilter."""


@admin.register(AssetLocation)
class AssetLocationAdmin(admin.ModelAdmin):
    class Media:
        """Necessary to use AutocompleteFilter."""

    formfield_overrides = {
        models.ManyToManyField: {"widget": CheckboxSelectMultiple},
    }


@admin.register(AssetLocationGroup)
class AssetLocationGroupAdmin(admin.ModelAdmin):
    class Media:
        """Necessary to use AutocompleteFilter."""

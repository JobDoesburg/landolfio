from django.contrib import admin
from django.forms import CheckboxSelectMultiple
from nested_admin.nested import NestedStackedInline
from nested_admin.polymorphic import NestedStackedPolymorphicInline, NestedPolymorphicModelAdmin

from asset_events.models import *
from asset_media.admin import AssetMediaItemInline
from assets.models import *
from maintenance.models import AssetReview, AssetMaintenanceTicket, AssetMaintenanceReturn, AssetAmortization
from asset_media.models import MediaSet
from purchases.models import SingleAssetPurchase, SingleAssetDelivery
from rentals.models import SingleUnprocessedAssetIssuance, SingleAssetLoan, SingleAssetRental, SingleAssetReturnal
from sales.models import SingleAssetSale


class AssetEventHistoryInline(NestedStackedPolymorphicInline):

    model = Event

    class AssetReviewEventInline(NestedStackedPolymorphicInline.Child):
        model = AssetReview

    class AssetMaintenanceTicketEventInline(NestedStackedPolymorphicInline.Child):
        model = AssetMaintenanceTicket

    class AssetMaintenanceReturnEventInline(NestedStackedPolymorphicInline.Child):
        model = AssetMaintenanceReturn

    class AssetAmortizationEventInline(NestedStackedPolymorphicInline.Child):
        model = AssetAmortization

    class AssetPurchaseEventInline(NestedStackedPolymorphicInline.Child):
        model = SingleAssetPurchase

    class AssetDeliveryEventInline(NestedStackedPolymorphicInline.Child):
        model = SingleAssetDelivery

    class UnprocessedAssetIssuanceEventInline(NestedStackedPolymorphicInline.Child):
        model = SingleUnprocessedAssetIssuance

    class AssetLoanEventInline(NestedStackedPolymorphicInline.Child):
        model = SingleAssetLoan

    class AssetRentalEventInline(NestedStackedPolymorphicInline.Child):
        model = SingleAssetRental

    class AssetReturnalEventInline(NestedStackedPolymorphicInline.Child):
        model = SingleAssetReturnal

    class AssetSaleEventInline(NestedStackedPolymorphicInline.Child):
        model = SingleAssetSale

    class AssetMiscellaneousAssetEventInline(NestedStackedPolymorphicInline.Child):
        model = MiscellaneousAssetEvent

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
        AssetMiscellaneousAssetEventInline,
    ]

    extra = 0

    classes = ["collapse"]


class AssetMediaInline(NestedStackedInline):
    model = MediaSet
    inlines = [AssetMediaItemInline]
    fields = ["date", "remarks", "event"]
    readonly_fields = ["event"]

    extra = 0
    classes = ["collapse"]


@admin.register(Asset)
class AssetAdmin(NestedPolymorphicModelAdmin):

    list_display = ["number", "category", "size", "status", "location"]
    list_filter = ["category", "status", "size", "location", "location__location_group"]

    readonly_fields = ["status"]

    search_fields = ["number", "event__memo"]

    inlines = [AssetMediaInline, AssetEventHistoryInline]

    def get_readonly_fields(self, request, obj=None):
        fields = super().get_readonly_fields(request, obj)
        try:
            fields += obj.get_immutable_fields()
        except Exception:
            pass
        return fields

    fieldsets = [
        ("Name", {"fields": ["number", "category", "size", "location", "retail_value", "status"]}),
    ]

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

from django.contrib import admin

from asset_events.admin import AssetForeignKeyAdmin, AssetForeignKeyStackedInline
from purchases.models.delivery import AssetDelivery, SingleAssetDelivery


class AssetDeliveryAssetInline(AssetForeignKeyStackedInline):  # TODO StatusChangingEventAdmin extend
    model = SingleAssetDelivery
    fk_name = "delivery"
    extra = 0


@admin.register(AssetDelivery)
class AssetSaleAdmin(AssetForeignKeyAdmin):
    inlines = [AssetDeliveryAssetInline]

    class Media:
        """Necessary to use AutocompleteFilter."""

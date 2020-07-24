from django.contrib import admin

from asset_events.admin import AssetForeignKeyAdmin
from purchases.admin.inlines import AssetDeliveryAssetInline
from purchases.models.delivery import AssetDelivery


@admin.register(AssetDelivery)
class AssetSaleAdmin(AssetForeignKeyAdmin):
    inlines = [AssetDeliveryAssetInline]

    class Media:
        """Necessary to use AutocompleteFilter."""

from django.contrib import admin

from asset_events.admin import AssetForeignKeyAdmin
from purchases.admin.inlines import AssetPurchaseAssetInline
from purchases.models.purchase import AssetPurchase


@admin.register(AssetPurchase)
class AssetSaleAdmin(AssetForeignKeyAdmin):
    inlines = [AssetPurchaseAssetInline]

    class Media:
        """Necessary to use AutocompleteFilter."""

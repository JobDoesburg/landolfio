from django.contrib import admin

from asset_events.admin import AssetForeignKeyAdmin, AssetForeignKeyStackedInline
from purchases.models.purchase import AssetPurchase, SingleAssetPurchase


class AssetPurchaseAssetInline(AssetForeignKeyStackedInline):  # TODO StatusChangingEventAdmin extend
    model = SingleAssetPurchase
    fk_name = "purchase"
    extra = 0


@admin.register(AssetPurchase)
class AssetSaleAdmin(AssetForeignKeyAdmin):
    inlines = [AssetPurchaseAssetInline]

    class Media:
        """Necessary to use AutocompleteFilter."""

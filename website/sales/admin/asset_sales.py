from django.contrib import admin

from asset_events.admin import AssetForeignKeyAdmin, AssetForeignKeyStackedInline
from sales.models import AssetSale, SingleAssetSale


class AssetSaleAssetInline(AssetForeignKeyStackedInline):  # TODO StatusChangingEventAdmin extend
    model = SingleAssetSale
    fk_name = "sale"
    extra = 0


@admin.register(AssetSale)
class AssetSaleAdmin(AssetForeignKeyAdmin):
    inlines = [AssetSaleAssetInline]

    class Media:
        """Necessary to use AutocompleteFilter."""

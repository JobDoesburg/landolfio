from django.contrib import admin

from asset_events.admin import AssetForeignKeyAdmin
from sales.admin.inlines import AssetSaleAssetInline
from sales.models import AssetSale


@admin.register(AssetSale)
class AssetSaleAdmin(AssetForeignKeyAdmin):
    inlines = [AssetSaleAssetInline]

    class Media:
        """Necessary to use AutocompleteFilter."""

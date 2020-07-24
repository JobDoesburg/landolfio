from django.contrib import admin

from asset_events.admin import AssetForeignKeyAdmin
from rentals.models.returnal import AssetReturnal
from rentals.admin.inlines import AssetReturnalAssetInline


@admin.register(AssetReturnal)
class AssetReturnalsAdmin(AssetForeignKeyAdmin):
    inlines = [AssetReturnalAssetInline]

    class Media:
        """Necessary to use AutocompleteFilter."""

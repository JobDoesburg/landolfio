from django.contrib import admin

from asset_events.admin import AssetForeignKeyAdmin, AssetForeignKeyStackedInline
from rentals.models.returnal import AssetReturnal, SingleAssetReturnal


class AssetReturnalAssetInline(AssetForeignKeyStackedInline):  # TODO StatusChangingEventAdmin extend
    model = SingleAssetReturnal
    fk_name = "returnal"
    extra = 0


@admin.register(AssetReturnal)
class AssetReturnalsAdmin(AssetForeignKeyAdmin):
    inlines = [AssetReturnalAssetInline]

    class Media:
        """Necessary to use AutocompleteFilter."""

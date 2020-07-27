from django.contrib import admin

from asset_events.admin import AssetForeignKeyAdmin
from assets.admin import AssetMediaInline
from maintenance.models.review import *


@admin.register(AssetReview)
class AssetReviewAdmin(AssetForeignKeyAdmin):
    class Media:
        """Necessary to use AutocompleteFilter."""

    inlines = [AssetMediaInline]

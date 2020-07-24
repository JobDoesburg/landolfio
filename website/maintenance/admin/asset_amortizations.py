from django.contrib import admin

from asset_events.admin import AssetForeignKeyAdmin
from maintenance.models.amortization import *


@admin.register(AssetAmortization)
class AssetAmortizationsAdmin(AssetForeignKeyAdmin):
    class Media:
        """Necessary to use AutocompleteFilter."""

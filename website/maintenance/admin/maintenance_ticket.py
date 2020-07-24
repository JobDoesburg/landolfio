from django.contrib import admin

from asset_events.admin import AssetForeignKeyAdmin
from maintenance.models.maintenance_ticket import *


@admin.register(AssetMaintenanceTicket)
class AssetMaintenanceTicketAdmin(AssetForeignKeyAdmin):
    class Media:
        """Necessary to use AutocompleteFilter."""


@admin.register(AssetMaintenanceReturn)
class AssetMaintenanceReturnAdmin(AssetForeignKeyAdmin):
    class Media:
        """Necessary to use AutocompleteFilter."""

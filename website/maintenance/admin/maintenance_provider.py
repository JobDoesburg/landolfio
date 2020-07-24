from django.contrib import admin

from maintenance.models import MaintenanceProvider


@admin.register(MaintenanceProvider)
class AssetMaintenanceTicketAdmin(admin.ModelAdmin):
    class Media:
        """Necessary to use AutocompleteFilter."""

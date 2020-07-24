from django.contrib import admin
from django.db.models import Q

from assets.models import Asset


class MaintenanceAsset(Asset):
    class Meta:
        proxy = True


@admin.register(MaintenanceAsset)
class MaintenanceAssetsAdmin(admin.ModelAdmin):
    list_display = ["number", "category", "size", "status"]
    list_filter = ["category", "size"]

    def get_queryset(self, request):
        return Asset.objects.filter(Q(status=Asset.MAINTENANCE_IN_HOUSE) | Q(status=Asset.MAINTENANCE_EXTERNAL))

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

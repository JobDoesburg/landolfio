from django.contrib import admin

from assets.models import Asset


class PlaceholderAsset(Asset):
    class Meta:
        proxy = True


@admin.register(PlaceholderAsset)
class PlaceholderAssetsAdmin(admin.ModelAdmin):
    list_display = ["number", "category", "size", "status"]
    list_filter = ["category", "size"]

    def get_queryset(self, request):
        return Asset.objects.filter(status=Asset.PLACEHOLDER)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

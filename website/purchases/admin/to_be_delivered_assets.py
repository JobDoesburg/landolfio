from django.contrib import admin

from assets.models import Asset


class ToBeDeliveredAsset(Asset):
    class Meta:
        proxy = True
        verbose_name = "asset to be delivered"
        verbose_name_plural = "assets to be delivered"


@admin.register(ToBeDeliveredAsset)
class ToBeDeliveredAssetsAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        return Asset.objects.filter(status=Asset.TO_BE_DELIVERED)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

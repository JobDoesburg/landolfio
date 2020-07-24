from django.contrib import admin

from assets.models import Asset


class UnprocessedIssuedAsset(Asset):
    class Meta:
        proxy = True
        verbose_name = "issued asset (unprocessed)"
        verbose_name_plural = "issued assets (unprocessed)"


@admin.register(UnprocessedIssuedAsset)
class UnprocessedIssuedAssetsAdmin(admin.ModelAdmin):
    list_display = ["number", "category", "size", "status"]
    list_filter = ["category", "size"]

    def get_queryset(self, request):
        return Asset.objects.filter(status=Asset.ISSUED_UNPROCESSED)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

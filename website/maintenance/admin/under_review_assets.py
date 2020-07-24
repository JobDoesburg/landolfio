from django.contrib import admin

from assets.models import Asset


class UnderReviewAsset(Asset):
    class Meta:
        proxy = True
        verbose_name = "asset under review"
        verbose_name_plural = "assets under review"


@admin.register(UnderReviewAsset)
class UnderReviewAssetsAdmin(admin.ModelAdmin):
    list_display = ["number", "category", "size", "status"]
    list_filter = ["category", "size"]

    def get_queryset(self, request):
        return Asset.objects.filter(status=Asset.UNDER_REVIEW)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

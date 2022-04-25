"""Inventory admin configuration."""
from django.contrib import admin

from .models import Asset
from .models import Collection


class AssetAdmin(admin.ModelAdmin):
    """Asset admin."""

    model = Asset
    list_display = (
        "id",
        "asset_type",
        "size",
        "collection",
        "listing_price",
        "stock_price",
    )


class CollectionAdmin(admin.ModelAdmin):
    """Collection admin."""

    model = Collection
    list_display = ("id", "name")


admin.site.register(Asset, AssetAdmin)
admin.site.register(Collection, CollectionAdmin)

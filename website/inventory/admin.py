"""Inventory admin configuration."""
from django.contrib import admin

from .models import Asset
from .models import AssetState


class AssetStateInlineAdmin(admin.StackedInline):
    """Asset state inline admin."""

    model = AssetState
    extra = 1


class AssetAdmin(admin.ModelAdmin):
    """Asset admin."""

    model = Asset
    list_display = ("asset_type", "size", "collection", "listing_price", "stock_price")
    inlines = [AssetStateInlineAdmin]


admin.site.register(Asset, AssetAdmin)

from django.contrib import admin
from django.db import models
from django.forms import CheckboxSelectMultiple

from assets.models.asset import Asset, AssetCategory, AssetSize
from assets.models.asset_location import AssetLocation, AssetLocationGroup


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):

    list_display = ["number", "category", "size", "status", "location", "collection", "tax_status"]
    list_filter = ["category", "status", "size", "location", "location__location_group", "collection", "tax_status"]

    search_fields = ["number"]

    fieldsets = [
        ("Name", {"fields": ["number", "category", "size", "location", "collection", "status"]}),
        ("Financial", {"fields": ["retail_value", "tax_status", "purchase_value", "current_stock_value", "sales_value"]}),
        ("Detail", {"fields": ["remarks",]}),
    ]

    readonly_fields = ["purchase_value", "current_stock_value", "sales_value"]

    class Media:
        """Necessary to use AutocompleteFilter."""


@admin.register(AssetCategory)
class AssetTypeAdmin(admin.ModelAdmin):
    class Media:
        """Necessary to use AutocompleteFilter."""


@admin.register(AssetSize)
class AssetSizeAdmin(admin.ModelAdmin):
    class Media:
        """Necessary to use AutocompleteFilter."""


@admin.register(AssetLocation)
class AssetLocationAdmin(admin.ModelAdmin):
    class Media:
        """Necessary to use AutocompleteFilter."""

    formfield_overrides = {
        models.ManyToManyField: {"widget": CheckboxSelectMultiple},
    }


@admin.register(AssetLocationGroup)
class AssetLocationGroupAdmin(admin.ModelAdmin):
    class Media:
        """Necessary to use AutocompleteFilter."""

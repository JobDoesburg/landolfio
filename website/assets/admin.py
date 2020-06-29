from django.contrib import admin

from assets.models import *


class AssetMemoInline(admin.StackedInline):
    """Inline form for Registration."""

    model = AssetMemo
    extra = 0


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):

    inlines = [AssetMemoInline]

    class Media:
        """Necessary to use AutocompleteFilter."""


@admin.register(AssetType)
class AssetTypeAdmin(admin.ModelAdmin):
    class Media:
        """Necessary to use AutocompleteFilter."""


@admin.register(AssetMemo)
class AssetMemoAdmin(admin.ModelAdmin):
    class Media:
        """Necessary to use AutocompleteFilter."""


@admin.register(AssetEvent)
class AssetEventAdmin(admin.ModelAdmin):
    class Media:
        """Necessary to use AutocompleteFilter."""


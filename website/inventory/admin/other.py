from django.contrib import admin
from django.db import models
from django.forms import CheckboxSelectMultiple
from inventory.models.attachment import Attachment
from inventory.models.category import AssetCategory, AssetSize
from inventory.models.collection import Collection
from inventory.models.location import AssetLocation, AssetLocationGroup


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    """Collection admin."""

    search_fields = ["name"]
    ordering = ["id"]


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    """Attachments admin."""

    model = Attachment
    list_display = ("asset", "attachment", "upload_date", "remarks")
    readonly_fields = ["upload_date"]


@admin.register(AssetCategory)
class AssetCategoryAdmin(admin.ModelAdmin):
    search_fields = ["name"]


@admin.register(AssetSize)
class AssetSizeAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.ManyToManyField: {"widget": CheckboxSelectMultiple},
    }
    search_fields = ["name"]


@admin.register(AssetLocation)
class AssetLocationAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.ManyToManyField: {"widget": CheckboxSelectMultiple},
    }

    search_fields = ["name"]


@admin.register(AssetLocationGroup)
class AssetLocationGroupAdmin(admin.ModelAdmin):
    search_fields = ["name"]

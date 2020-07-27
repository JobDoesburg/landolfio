from django.contrib import admin
from django.utils.safestring import mark_safe
from nested_admin.nested import NestedStackedInline, NestedModelAdmin

from asset_media.models import MediaSet, MediaItem


class AssetMediaItemInline(NestedStackedInline):
    model = MediaItem
    fk_name = "set"
    extra = 0
    fields = ["thumbnail", "media"]
    readonly_fields = ["thumbnail"]

    def thumbnail(self, obj):
        return mark_safe(
            '<a href={url} target="_blank"><img src="{url}" width="{width}" /></a>'.format(
                url=obj.media.url, width=400,
            )
        )


@admin.register(MediaSet)
class MediaSetAdmin(NestedModelAdmin):
    inlines = [AssetMediaItemInline]

    class Media:
        """Necessary to use AutocompleteFilter."""


@admin.register(MediaItem)
class MediaItemAdmin(admin.ModelAdmin):
    fields = ["set", "media", "file"]
    readonly_fields = ["file"]

    def file(self, obj):
        return mark_safe(
            '<a href={url} target="_blank"><img src="{url}" width="{width}"/></a>'.format(
                url=obj.media.url, width=1080,
            )
        )

    class Media:
        """Necessary to use AutocompleteFilter."""

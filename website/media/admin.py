from django.contrib import admin

from media.models import MediaSet, MediaItem


class MediaItemInline(admin.TabularInline):
    """Inline form for Registration."""

    model = MediaItem
    extra = 10


@admin.register(MediaSet)
class MediaSetAdmin(admin.ModelAdmin):
    inlines = [MediaItemInline]

    class Media:
        """Necessary to use AutocompleteFilter."""

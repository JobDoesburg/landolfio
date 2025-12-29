from django.contrib import admin

from scantags.models import ScanTag


@admin.register(ScanTag)
class ScanTagAdmin(admin.ModelAdmin):
    search_fields = ["id", "asset"]
    ordering = ["id"]
    list_display = ["id", "asset"]
    autocomplete_fields = ["asset"]

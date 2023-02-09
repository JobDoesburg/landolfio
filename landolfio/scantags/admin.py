from django.contrib import admin
from scantags.models import ScanTag


class ScanTagAdmin(admin.ModelAdmin):
    model = ScanTag

    search_fields = ["id", "asset"]
    ordering = ["id"]
    list_display = ["id", "asset"]
    autocomplete_fields = ["asset"]

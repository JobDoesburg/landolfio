"""Accounting admin configuration."""
from django.contrib import admin

from .models import Document
from .models import DocumentLine


class DocumentLineAdmin(admin.TabularInline):
    """The admin view for DocumentLines."""

    model = DocumentLine
    fields = ("asset_id_field", "asset", "ledger")


class DocumentAdmin(admin.ModelAdmin):
    """The admin view for Documents."""

    inlines = (DocumentLineAdmin,)


admin.site.register(Document, DocumentAdmin)

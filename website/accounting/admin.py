"""Accounting admin configuration."""
from django.contrib import admin

from .models import Document
from .models import DocumentLine
from .models import Ledger


class LedgerAdmin(admin.ModelAdmin):
    """The Django admin config for the Ledger model."""

    model = Ledger
    list_display = ("kind", "moneybird_id")


class DocumentLineAdmin(admin.TabularInline):
    """The admin view for DocumentLines."""

    model = DocumentLine
    fields = ("asset_id_field", "asset", "ledger")


class DocumentAdmin(admin.ModelAdmin):
    """The admin view for Documents."""

    inlines = (DocumentLineAdmin,)

    def has_add_permission(self, request):
        """Prevent all users from adding Documents."""
        return False

    def has_change_permission(self, request, obj=None):
        """Prevent all users from changing Documents."""
        return False


admin.site.register(Ledger, LedgerAdmin)
admin.site.register(Document, DocumentAdmin)

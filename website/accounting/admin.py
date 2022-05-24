"""Accounting admin configuration."""
from django.contrib import admin

from .models import Document
from .models import DocumentLine
from .models import Ledger

admin.site.register(Document)
admin.site.register(DocumentLine)


class LedgerAdmin(admin.ModelAdmin):
    """The Django admin config for the Ledger model."""

    model = Ledger
    list_display = ("kind", "moneybird_id")


admin.site.register(Ledger, LedgerAdmin)

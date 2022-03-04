"""Accounting admin configuration."""
from assets.models import Asset
from django.contrib import admin

from .models import Invoice
from .models import Receipt


class AssetInlineAdmin(admin.StackedInline):
    """Asset inline admin."""

    model = Asset


class ReceiptAdmin(admin.ModelAdmin):
    """Receipt admin."""

    model = Receipt
    inlines = [AssetInlineAdmin]


class InvoiceAdmin(admin.ModelAdmin):
    """Invoice admin."""

    model = Invoice
    inlines = [AssetInlineAdmin]


admin.site.register(Receipt, ReceiptAdmin)
admin.site.register(Invoice, InvoiceAdmin)

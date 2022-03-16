"""Accounting admin configuration."""
from django.contrib import admin

from .models import Invoice
from .models import Receipt


class ReceiptAdmin(admin.ModelAdmin):
    """Receipt admin."""

    model = Receipt


class InvoiceAdmin(admin.ModelAdmin):
    """Invoice admin."""

    model = Invoice


admin.site.register(Receipt, ReceiptAdmin)
admin.site.register(Invoice, InvoiceAdmin)

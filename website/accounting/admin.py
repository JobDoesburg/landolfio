"""Accounting admin configuration."""
from django.contrib import admin

from .models import Document
from .models import DocumentLine

admin.site.register(Document)
admin.site.register(DocumentLine)

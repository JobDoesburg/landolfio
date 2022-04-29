"""Inventory admin configuration."""
from accounting.models import Document
from django.contrib import admin

from .models import Asset
from .models import AssetState


class AssetStateInlineAdmin(admin.StackedInline):
    """Asset state inline admin."""

    model = AssetState
    extra = 1


class AssetAdmin(admin.ModelAdmin):
    """Asset admin."""

    model = Asset
    list_display = ("asset_type", "size", "collection", "listing_price", "stock_price")
    inlines = [AssetStateInlineAdmin]

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        """Render the change page for an Asset."""
        if extra_context is None:
            extra_context = {}

        asset = Asset.objects.get(pk=object_id)
        related_document_ids = asset.documentline_set.values_list("document", flat=True)
        related_documents = Document.objects.filter(pk__in=set(related_document_ids))

        extra_context["related_documents"] = related_documents

        return super().changeform_view(request, object_id, form_url, extra_context)


admin.site.register(Asset, AssetAdmin)

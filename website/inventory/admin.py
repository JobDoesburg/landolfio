"""Inventory admin configuration."""
from accounting.models import Document
from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist

from .models import Asset
from .models import Collection


class AssetAdmin(admin.ModelAdmin):
    """Asset admin."""

    model = Asset
    list_display = (
        "id",
        "asset_type",
        "size",
        "collection",
        "listing_price",
        "stock_price",
    )


class CollectionAdmin(admin.ModelAdmin):
    """Collection admin."""

    model = Collection
    list_display = ("id", "name")

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        """Render the change page for an Asset."""
        if extra_context is None:
            extra_context = {}

        try:
            asset = Asset.objects.get(pk=object_id)
            related_document_ids = asset.documentline_set.values_list(
                "document", flat=True
            )
            related_documents = Document.objects.filter(
                pk__in=set(related_document_ids)
            )
        except ObjectDoesNotExist:
            related_documents = None

        extra_context["related_documents"] = related_documents

        return super().changeform_view(request, object_id, form_url, extra_context)


admin.site.register(Asset, AssetAdmin)
admin.site.register(Collection, CollectionAdmin)

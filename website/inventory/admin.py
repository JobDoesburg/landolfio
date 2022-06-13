"""Inventory admin configuration."""
from accounting.models import Document
from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

from .models import Asset
from .models import Attachment
from .models import Collection


def is_an_image_path(path: str) -> bool:
    """Return true if the path points to an image."""
    extension = path.split(".")[-1]
    return extension in ("jpg", "jpeg", "png")


class AttachmentInlineAdmin(admin.StackedInline):
    """Attachment inline admin."""

    def show_image(self, obj):
        # pylint: disable=no-self-use
        """Show a file as an image if it is one."""
        if is_an_image_path(obj.attachment.name):
            return mark_safe(f'<img src="{obj.attachment.url}" height="600px"/>')
        return _("Not an image")

    show_image.short_description = _("Image")

    model = Attachment
    readonly_fields = ["show_image", "upload_date"]
    extra = 0


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
    inlines = [AttachmentInlineAdmin]

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


class CollectionAdmin(admin.ModelAdmin):
    """Collection admin."""

    model = Collection
    list_display = ("id", "name")


class AttachmentAdmin(admin.ModelAdmin):
    """Attachments admin."""

    model = Attachment
    list_display = ("asset", "attachment", "upload_date", "remarks")
    readonly_fields = ["upload_date"]


admin.site.register(Asset, AssetAdmin)
admin.site.register(Collection, CollectionAdmin)
admin.site.register(Attachment, AttachmentAdmin)

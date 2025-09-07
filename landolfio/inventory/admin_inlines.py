from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from inventory.models.attachment import Attachment
from inventory.models.remarks import Remark


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


class RemarkInline(admin.StackedInline):
    model = Remark
    fields = ["date", "remark"]
    readonly_fields = ["date"]
    extra = 1

    def has_change_permission(self, request, obj=None):
        return False

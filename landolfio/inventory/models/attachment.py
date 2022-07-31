from django.db import models

from inventory.models.asset import Asset
from django.utils.translation import gettext_lazy as _


def attachments_directory_path(instance, filename):
    """Return the attachment's directory path."""
    return f"inventory/attachments/{instance.asset.id}/{filename}"


class Attachment(models.Model):
    """Class model for Attachments."""

    asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE,
        verbose_name=_("Asset"),
        related_name="attachments",
    )
    attachment = models.FileField(
        upload_to=attachments_directory_path,
        verbose_name=_("Attachment"),
    )
    upload_date = models.DateField(auto_now_add=True, verbose_name=_("Upload date"))

    def __str__(self):
        """Return Attachment string."""
        return f"{self.attachment} from {self.asset}"

    class Meta:
        """Meta Class to define verbose_name."""

        verbose_name = "Bijlage"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.attachment:
            self._orig_image = self.attachment.name
        else:
            self._orig_image = None

    def delete(self, using=None, keep_parents=False):
        if self.attachment.name:
            self.attachment.delete()
        return super().delete(using, keep_parents)

    def save(self, **kwargs):
        super().save(**kwargs)
        storage = self.attachment.storage

        if self._orig_image and self._orig_image != self.attachment.name:
            storage.delete(self._orig_image)
            self._orig_image = None

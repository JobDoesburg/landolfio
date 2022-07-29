from django.db import models

from inventory.models.asset import Asset
from django.utils.translation import gettext_lazy as _


def attachments_directory_path(instance, filename):
    """Return the attachment's directory path."""
    return f"inventory/attachments/{instance.asset.id}/{filename}"


class Attachment(models.Model):
    """Class model for Attachments."""

    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, verbose_name=_("Asset"))
    attachment = models.FileField(
        upload_to=attachments_directory_path, verbose_name=_("Attachment")
    )
    upload_date = models.DateField(auto_now_add=True, verbose_name=_("Upload date"))

    def __str__(self):
        """Return Attachment string."""
        return f"{self.attachment} from {self.asset}"

    class Meta:
        """Meta Class to define verbose_name."""

        verbose_name = "Bijlage"

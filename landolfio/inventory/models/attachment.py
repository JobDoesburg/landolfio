from django.db import models

from inventory.models.asset import Asset
from django.utils.translation import gettext_lazy as _


def attachments_directory_path(instance, filename):
    return f"inventory/attachments/{instance.asset.id}/{filename}"


class Attachment(models.Model):
    asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE,
        verbose_name=_("asset"),
        related_name="attachments",
    )
    attachment = models.FileField(
        upload_to=attachments_directory_path,
        verbose_name=_("attachment"),
    )
    upload_date = models.DateField(auto_now_add=True, verbose_name=_("upload date"))

    def __str__(self):
        return f"{self.attachment} {_('from')} {self.asset}"

    class Meta:
        verbose_name = _("attachment")
        verbose_name_plural = _("attachments")
        ordering = ["upload_date"]

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

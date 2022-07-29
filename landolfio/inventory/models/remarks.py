from django.db import models

from inventory.models.asset import Asset
from django.utils.translation import gettext_lazy as _


class Remark(models.Model):
    """Class model for Attachments."""

    asset = models.ForeignKey(
        Asset, on_delete=models.CASCADE, related_name="remarks", verbose_name=_("Asset")
    )
    remark = models.TextField(verbose_name=_("Remark"))
    date = models.DateField(auto_now_add=True, verbose_name=_("date"))

    def __str__(self):
        """Return Attachment string."""
        return f"Remark on {self.asset} ({self.date:%d-%m-%Y})"

    class Meta:
        """Meta Class to define verbose_name."""

        verbose_name = "Remark"

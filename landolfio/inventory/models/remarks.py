from django.db import models

from inventory.models.asset import Asset
from django.utils.translation import gettext_lazy as _


class Remark(models.Model):
    asset = models.ForeignKey(
        Asset, on_delete=models.CASCADE, related_name="remarks", verbose_name=_("asset")
    )
    remark = models.TextField(verbose_name=_("remark"))
    date = models.DateField(auto_now_add=True, verbose_name=_("date"))

    def __str__(self):
        return f"{_('Remark on')} {self.asset} ({self.date:%d-%m-%Y})"

    class Meta:
        verbose_name = _("remark")
        verbose_name_plural = _("remarks")

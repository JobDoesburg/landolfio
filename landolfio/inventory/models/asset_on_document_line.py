from django.db import models
from django.utils.translation import gettext_lazy as _

from accounting.models import Subscription


class AssetSubscription(models.Model):
    asset = models.ForeignKey(
        "Asset",
        on_delete=models.CASCADE,
        related_name="asset_subscriptions",
        verbose_name=_("asset"),
    )
    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.CASCADE,
        related_name="assets",
        verbose_name=_("subscription"),
    )
    value = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name=_("value")
    )

    class Meta:
        verbose_name = _("asset subscription")
        verbose_name_plural = _("assets subscriptions")
        unique_together = [
            ("asset", "subscription"),
        ]

    def __str__(self):
        return f"{self.asset} {_('on')} {self.subscription} [{self.value}]"

from django.db import models
from django.utils.translation import gettext_lazy as _

from inventory.models.asset import AssetStates


class StatusChange(models.Model):
    """Model to track status changes for assets with history."""

    asset = models.ForeignKey(
        "Asset",
        on_delete=models.CASCADE,
        related_name="status_changes",
        verbose_name=_("asset"),
    )

    new_status = models.CharField(
        max_length=40,
        choices=AssetStates.choices,
        null=True,
        blank=True,
        verbose_name=_("new status"),
        help_text=_("The status the asset changed to, or null for no status change"),
    )

    status_date = models.DateField(
        verbose_name=_("status date"),
        help_text=_("The date when this status change occurred"),
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("created at"),
        help_text=_("When this status change was recorded in the system"),
    )

    comments = models.TextField(
        blank=True,
        verbose_name=_("comments"),
        help_text=_("Optional comments about this status change"),
    )

    contact = models.ForeignKey(
        "accounting.Contact",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="status_changes",
        verbose_name=_("contact"),
        help_text=_("Moneybird contact associated with this status change"),
    )

    class Meta:
        ordering = ["status_date", "created_at"]
        verbose_name = _("status change")
        verbose_name_plural = _("status changes")

        # Ensure we can efficiently query the latest status change
        indexes = [
            models.Index(fields=["asset", "-status_date", "-created_at"]),
        ]

    def __str__(self):
        return (
            f"{self.asset.name} → {self.get_new_status_display()} ({self.status_date})"
        )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Update the asset's cached current status
        if hasattr(self.asset, "_current_status_cache"):
            del self.asset._current_status_cache

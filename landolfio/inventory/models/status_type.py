from django.db import models
from django.utils.translation import gettext_lazy as _


class StatusType(models.Model):
    """
    Defines available status types for assets.

    This replaces the hardcoded AssetStates choices with a flexible model.
    """

    slug = models.SlugField(
        max_length=40,
        primary_key=True,
        verbose_name=_("slug"),
        help_text=_(
            "Unique identifier used in code (e.g., 'available', 'issued_rent')"
        ),
    )

    name = models.CharField(
        max_length=100,
        verbose_name=_("name"),
        help_text=_("Display name for this status"),
    )

    background_color = models.CharField(
        max_length=7,
        verbose_name=_("background color"),
        default="#0d6efd",
        help_text=_("Hex color code for background (e.g., '#198754' for green)"),
    )

    text_color = models.CharField(
        max_length=7,
        verbose_name=_("text color"),
        default="#ffffff",
        help_text=_("Hex color code for text (e.g., '#ffffff' for white)"),
    )

    is_archived = models.BooleanField(
        default=False,
        verbose_name=_("is archived"),
        help_text=_(
            "Indicates if this status means the asset is archived/no longer active"
        ),
    )

    order = models.IntegerField(
        default=0,
        verbose_name=_("order"),
        help_text=_("Display order in lists and dropdowns"),
    )

    class Meta:
        ordering = ["order", "name"]
        verbose_name = _("status type")
        verbose_name_plural = _("status types")

    def __str__(self):
        return self.name

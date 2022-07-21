from django.db import models
from django.utils.translation import gettext_lazy as _


class Collection(models.Model):
    """Class model for an asset collection."""

    name = models.CharField(
        verbose_name=_("Collection Name"), max_length=200, unique=True
    )

    commerce = models.BooleanField()

    def __str__(self):
        """Return Asset string."""
        return f"{self.name}"

    class Meta:
        """Meta Class to define verbose_name."""

        verbose_name = "Collectie"

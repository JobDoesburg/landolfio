"""The accounting models."""
from django.db import models
from django.utils.translation import gettext as _

from .moneybird.get_changes import DOCUMENT_KINDS
from .moneybird.get_changes import name_for_kind


class Document(models.Model):
    """Class model for Documents."""

    id_MB = models.IntegerField(verbose_name=_("Id MoneyBird"))
    json_MB = models.JSONField(verbose_name=_("JSON MoneyBird"))
    kind = models.CharField(
        max_length=2, choices=[(kind, name_for_kind(kind)) for kind in DOCUMENT_KINDS]
    )

    def __str__(self):
        """Return Document string."""
        return f"{str(self.kind)}_{str(self.id)}"

    class Meta:
        """
        The meta-variables for the Document model.

        As the MoneyBird API documentation does not clearly specify whether Document
        IDs are globally unique or just unique for one Document Kind, we must assume
        the latter.
        """

        unique_together = ("id_MB", "kind")

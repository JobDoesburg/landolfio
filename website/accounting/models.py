"""The accounting models."""
from django.db import models
from django.utils.translation import gettext as _

from .moneybird.get_changes import DocKind


class Document(models.Model):
    """Class model for Documents."""

    id_MB = models.IntegerField(verbose_name=_("Id MoneyBird"))
    json_MB = models.JSONField(verbose_name=_("JSON MoneyBird"))
    kind = models.CharField(max_length=2, choices=DocKind.choices)

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


class DocumentLine(models.Model):
    """A line in a document."""

    json_MB = models.JSONField(verbose_name=_("JSON MoneyBird"))
    document = models.ForeignKey(
        Document, on_delete=models.CASCADE, verbose_name=_("Document")
    )

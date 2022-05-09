"""The accounting models."""
from django.db import models
from django.utils.translation import gettext as _
from inventory.models import Asset

from .moneybird.get_changes import DocKind

Ledgers = (
    ("Voorraad marge", _("Voorraad marge")),
    ("Voorraad niet-marge", _("Voorraad niet-marge")),
    ("Voorraadwaarde bij verkoop marge", _("Voorraadwaarde bij verkoop marge")),
    (
        "Voorraadwaarde bij verkoop niet-marge",
        _("Voorraadwaarde bij verkoop niet-marge"),
    ),
    ("Verkoop marge", _("Verkoop marge")),
    ("Verkoop niet-marge", _("Verkoop niet-marge")),
    ("Directe afschrijving bij aankoop", _("Directe afschrijving bij aankoop")),
    ("Afschrijvingen", _("Afschrijvingen")),
    ("Borgen", _("Borgen")),
)


class Document(models.Model):
    """Class model for Documents."""

    id_MB = models.PositiveBigIntegerField(verbose_name=_("Id MoneyBird"))
    json_MB = models.JSONField(verbose_name=_("JSON MoneyBird"))
    kind = models.CharField(max_length=2, choices=DocKind.choices)

    @property
    def moneybird_url(self) -> str:
        """Return the moneybird url."""
        kind = DocKind(self.kind)
        adm_id = self.json_MB["administration_id"]
        doc_id = self.json_MB["id"]
        return f"https://moneybird.com/{adm_id}/{kind.user_path}/{doc_id}"

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
    ledger = models.CharField(max_length=40, choices=Ledgers, null=True, blank=True)
    document = models.ForeignKey(
        Document, on_delete=models.CASCADE, verbose_name=_("Document")
    )
    asset = models.ForeignKey(
        Asset, null=True, on_delete=models.SET_NULL, verbose_name=_("Asset")
    )

    def __str__(self):
        """Format a DocumentLine as a human readable string."""
        return f"Line in {self.document} with asset {self.asset_id}"

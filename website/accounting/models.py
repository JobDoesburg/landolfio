"""The accounting models."""
from django.db import models
from django.utils.translation import gettext as _

from .moneybird.get_changes import DocKind


class LedgerKind(models.TextChoices):
    """A kind of ledger."""

    VOORRAAD_MARGE = "VOORRAAD_MARGE", "Voorraad Marge"
    VOORRAAD_NIET_MARGE = "VOORRAAD_NIET_MARGE", "Voorraad niet-marge"
    VOORRAAD_BIJ_VERKOOP_MARGE = (
        "VOORRAAD_BIJ_VERKOOP_MARGE",
        "Voorraadwaarde bij verkoop marge",
    )
    VOORRAAD_BIJ_VERKOOP_NIET_MARGE = (
        "VOORRAAD_BIJ_VERKOOP_NIET_MARGE",
        "Voorraadwaarde bij verkoop niet-marge",
    )
    VERKOOP_MARGE = "VERKOOP_MARGE", "Verkoop marge"
    VERKOOP_NIET_MARGE = "VERKOOP_NIET_MARGE", "Verkoop niet-marge"
    DIRECTE_AFSCHRIJVING = "DIRECTE_AFSCHRIJVING", "Directe afschrijving"
    AFSCHRIJVINGEN = "AFSCHRIJVINGEN", "Afschrijvingen"
    BORGEN = "BORGEN", "Borgen"


class Ledger(models.Model):
    """A ledger."""

    moneybird_id = models.PositiveBigIntegerField(
        primary_key=True, verbose_name=_("Id MoneyBird")
    )
    kind = models.CharField(
        max_length=100,
        choices=LedgerKind.choices,
        null=True,
        unique=True,
        verbose_name=_("Kind"),
    )

    def __str__(self):
        """Return a human-readable string for a Ledger."""
        if not self.kind:
            return str(self.moneybird_id)

        return LedgerKind(self.kind).label

    class Meta:
        """Meta Class to define verbose_name."""

        verbose_name = "Grootboekrekening"
        verbose_name_plural = "Grootboekrekeningen"


class Document(models.Model):
    """Class model for Documents."""

    moneybird_id = models.PositiveBigIntegerField(verbose_name=_("Id MoneyBird"))
    moneybird_json = models.JSONField(verbose_name=_("JSON MoneyBird"))
    kind = models.CharField(
        max_length=2, choices=DocKind.choices, verbose_name=_("Kind")
    )

    @property
    def moneybird_url(self) -> str:
        """Return the moneybird url."""
        kind = DocKind(self.kind)
        adm_id = self.moneybird_json["administration_id"]
        doc_id = self.moneybird_json["id"]
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

        unique_together = ("moneybird_id", "kind")
        verbose_name_plural = "Documenten"


class DocumentLine(models.Model):
    """A line in a document."""

    moneybird_json = models.JSONField(verbose_name=_("JSON MoneyBird"))
    ledger = models.ForeignKey(
        Ledger, on_delete=models.PROTECT, verbose_name=_("Ledger")
    )
    price = models.DecimalField(
        max_digits=19, decimal_places=4, verbose_name=_("Price")
    )
    document = models.ForeignKey(
        Document, on_delete=models.CASCADE, verbose_name=_("Document")
    )
    asset_id_field = models.CharField(
        max_length=50, null=True, verbose_name=_("Asset Id")
    )
    asset = models.ForeignKey(
        "inventory.Asset", null=True, on_delete=models.SET_NULL, verbose_name=_("Asset")
    )

    def __str__(self):
        """Format a DocumentLine as a human readable string."""
        return f"Line in {self.document} with asset {self.asset_id}"

    class Meta:
        """Meta Class to define verbose_name."""

        verbose_name = "Documentregel"

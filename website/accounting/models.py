"""The accounting models."""
from enum import IntEnum

from django.db import models
from django.utils.functional import classproperty
from django.utils.translation import gettext as _
from inventory.models import Asset

from .moneybird.get_changes import DocKind


class LedgerAccountId(IntEnum):
    """ "
    Enum to translate legder account ids to python enum

    The integer value on the right side is the moneybird ledger account id. These values may be different per administration
    """

    VOORRAAD_MARGE = 340246234795083709
    VOORRAAD_NIET_MARGE = 340246538381952245
    VOORRAAD_BIJ_VERKOOP_MARGE = 340245783921034390
    VOORRAAD_BIJ_VERKOOP_NIET_MARGE = 340246576039462518
    VERKOOP_MARGE = 340245854757586711
    VERKOOP_NIET_MARGE = 340246558119298417
    DIRECTE_AFSCHRIJVING = 6
    AFSCHRIJVINGEN = 340246156081628510
    BORGEN = 340246430358701525
    UNKNOWN = -1

    @property
    def human_readable_name(self):
        if self == LedgerAccountId.VOORRAAD_MARGE:
            return _("Voorraad marge")
        if self == LedgerAccountId.VOORRAAD_NIET_MARGE:
            return _("Voorraad niet-marge")
        if self == LedgerAccountId.VOORRAAD_BIJ_VERKOOP_MARGE:
            return _("Voorraadwaarde bij verkoop marge")
        if self == LedgerAccountId.VOORRAAD_BIJ_VERKOOP_NIET_MARGE:
            return _("Voorraadwaarde bij verkoop niet-marge")
        if self == LedgerAccountId.VERKOOP_MARGE:
            return _("Verkoop marge")
        if self == LedgerAccountId.VERKOOP_NIET_MARGE:
            return _("Verkoop niet-marge")
        if self == LedgerAccountId.DIRECTE_AFSCHRIJVING:
            return _("Directe afschrijving bij aankoop")
        if self == LedgerAccountId.AFSCHRIJVINGEN:
            return _("Afschrijvingen")
        if self == LedgerAccountId.BORGEN:
            return _("Borgen")
        if self == LedgerAccountId.UNKNOWN:
            return _("Unknown")

        raise NotImplementedError(
            f"The human readable name for ledger account id '{self}' is not yet defined."
        )

    @classproperty
    def choices(cls):
        """Create a (name, human_readable_name) list for Django choices"""
        return [(e.name, e.human_readable_name) for e in cls]

    def translate(ledger_id: int):
        """ "Translate ledger ids to enum, return unknown if not found"""
        for e in LedgerAccountId:
            if e.value == ledger_id:
                return e

        return LedgerAccountId.UNKNOWN


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
    ledger = models.CharField(
        max_length=100, choices=LedgerAccountId.choices, default=LedgerAccountId.UNKNOWN
    )
    document = models.ForeignKey(
        Document, on_delete=models.CASCADE, verbose_name=_("Document")
    )
    asset = models.ForeignKey(
        Asset, null=True, on_delete=models.SET_NULL, verbose_name=_("Asset")
    )

    def __str__(self):
        """Format a DocumentLine as a human readable string."""
        return f"Line in {self.document} with asset {self.asset_id}"

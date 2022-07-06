from django.db import models
from django.utils.translation import gettext as _


class MoneybirdResourceModel(models.Model):
    moneybird_id = models.PositiveBigIntegerField(verbose_name=_("Id MoneyBird"))

    class Meta:
        abstract = True


class SynchronizableMoneybirdResourceModel(MoneybirdResourceModel):
    version = models.PositiveBigIntegerField(verbose_name=_("version"))

    class Meta:
        abstract = True


class Contact(SynchronizableMoneybirdResourceModel):
    moneybird_json = models.JSONField(verbose_name=_("JSON MoneyBird"))


class LedgerKind(models.TextChoices):
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


class Ledger(MoneybirdResourceModel):
    name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
    )

    ledger_kind = models.CharField(
        max_length=100,
        choices=LedgerKind.choices,
        null=True,
        unique=True,
        verbose_name=_("Kind"),
    )

    def __str__(self):
        if not self.ledger_kind:
            return str(self.moneybird_id)
        return LedgerKind(self.ledger_kind).label

    class Meta:
        verbose_name = "Grootboekrekening"
        verbose_name_plural = "Grootboekrekeningen"


class DocumentKind(models.TextChoices):
    SALES_INVOICE = "FAC", _("Sales invoice")
    PURCHASE_INVOICE = "INK", _("Purchase invoice")
    RECEIPT = "BON", _("Receipt")
    GENERAL_JOURNAL_DOCUMENT = "MEM", _("General journal document")


class JournalDocument(SynchronizableMoneybirdResourceModel):
    date = models.DateField()
    moneybird_json = models.JSONField(verbose_name=_("JSON MoneyBird"))
    document_kind = models.CharField(
        max_length=3, choices=DocumentKind.choices, verbose_name=_("document kind")
    )

    def __str__(self):
        if self.document_kind == DocumentKind.SALES_INVOICE:
            return f"FAC {self.moneybird_json['invoice_id']}"
        else:
            return f"{self.document_kind} {self.moneybird_json['reference']}"

    class Meta:
        unique_together = ("moneybird_id", "document_kind")
        verbose_name_plural = "Documenten"
        ordering = ("date",)


class DocumentLine(MoneybirdResourceModel):
    moneybird_json = models.JSONField(verbose_name=_("JSON MoneyBird"))
    ledger = models.ForeignKey(
        Ledger, on_delete=models.PROTECT, verbose_name=_("Ledger")
    )
    price = models.DecimalField(
        max_digits=19, decimal_places=4, verbose_name=_("Price")
    )
    document = models.ForeignKey(
        JournalDocument, on_delete=models.CASCADE, verbose_name=_("Document")
    )
    asset_id_field = models.CharField(
        max_length=50, null=True, verbose_name=_("Asset Id")
    )
    asset = models.ForeignKey(
        "inventory.Asset",
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Asset"),
        related_name="document_lines",
    )

    def __str__(self):
        return f"Line in {self.document} with asset {self.asset_id}"

    class Meta:
        verbose_name = "Documentregel"
        ordering = ("document__date",)


class Subscription(MoneybirdResourceModel):
    moneybird_json = models.JSONField(verbose_name=_("JSON MoneyBird"))


class Product(MoneybirdResourceModel):
    moneybird_json = models.JSONField(verbose_name=_("JSON MoneyBird"))

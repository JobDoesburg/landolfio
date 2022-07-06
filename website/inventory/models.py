"""Asset models."""
import re
from typing import Union

from django.core.validators import validate_unicode_slug
from django.db import models
from django.db.models import Sum, PROTECT
from django.dispatch import receiver
from django.utils.translation import gettext as _

from accounting.models import (
    DocumentKind,
    JournalDocumentLine,
    EstimateDocumentLine,
    LedgerKind,
    Ledger,
)

Asset_States = (
    ("Unknown", _("Unknown")),
    ("N/A", _("N/A")),
    ("Purchased", _("Purchased")),
    ("Sold", _("Sold")),
    ("Sold (incomplete)", _("Sold (incomplete)")),
    ("Sold (error)", _("Sold (error)")),
    ("Rented", _("Rented")),
    ("Rented (error)", _("Rented (error)")),
    ("Loaned", _("Loaned")),
    ("Amortized", _("Amortized")),
)

Estimates = (
    ("Huurovereenkomst", _("Huurovereenkomst")),
    ("Leenovereenkomst", _("Leenovereenkomst")),
)


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


class AssetCategory(models.Model):
    class Meta:
        verbose_name = "category"
        verbose_name_plural = "categories"

    name = models.CharField(null=False, blank=False, max_length=20)
    name_singular = models.CharField(
        null=False, blank=False, max_length=20, validators=[validate_unicode_slug]
    )

    def __str__(self):
        return f"{self.name}"


class AssetSize(models.Model):
    class Meta:
        verbose_name = "size"
        verbose_name_plural = "sizes"

    name = models.CharField(null=False, blank=False, max_length=20)
    categories = models.ManyToManyField(AssetCategory, blank=False)

    def __str__(self):
        return f"{self.name}"


class AssetLocationGroup(models.Model):
    class Meta:
        verbose_name = "location group"
        verbose_name_plural = "location groups"

    name = models.CharField(null=False, blank=False, max_length=20)

    def __str__(self):
        return self.name


class AssetLocation(models.Model):
    class Meta:
        verbose_name = "location"
        verbose_name_plural = "locations"

    name = models.CharField(null=False, blank=False, max_length=20)
    location_group = models.ForeignKey(
        AssetLocationGroup, blank=False, null=False, on_delete=PROTECT
    )

    def __str__(self):
        return f"{self.name} ({self.location_group})"


class Asset(models.Model):
    """Class model for Assets."""

    id = models.CharField(verbose_name=_("ID"), max_length=200, primary_key=True)
    category = models.ForeignKey(
        AssetCategory, null=True, blank=False, on_delete=PROTECT
    )
    size = models.ForeignKey(AssetSize, null=True, blank=True, on_delete=PROTECT)
    location = models.ForeignKey(
        AssetLocation, null=True, blank=True, on_delete=PROTECT
    )
    collection = models.ForeignKey(
        Collection, on_delete=models.CASCADE, verbose_name=_("Collection")
    )

    listing_price = models.FloatField(verbose_name=_("Listing price"))
    stock_price = models.FloatField(verbose_name=_("Stock price"))
    purchasing_value = models.FloatField(verbose_name=_("Purchasing value"))
    remarks = models.TextField(
        verbose_name=_("Remarks"), max_length=1000, null=True, blank=True
    )
    moneybird_state = models.CharField(
        max_length=40,
        choices=Asset_States,
        verbose_name=_("Moneybird State"),
        default="Unknown",
    )
    local_state = models.CharField(
        max_length=40,
        choices=Asset_States,
        verbose_name=_("Local State"),
        default="Unknown",
    )

    @property
    def ledger_amounts(self):
        return dict(
            (
                Ledger.objects.get(moneybird_id=x["ledger__moneybird_id"]),
                x["price__sum"],
            )
            for x in self.document_lines.values("ledger__moneybird_id").annotate(
                Sum("price")
            )
        )

    @property
    def stock_value(self):
        return self.ledger_amounts.get(
            Ledger.objects.get(ledger_kind=LedgerKind.VOORRAAD_NIET_MARGE), 0
        ) + self.ledger_amounts.get(
            Ledger.objects.get(ledger_kind=LedgerKind.VOORRAAD_MARGE), 0
        )

    @property
    def sales_value(self):
        return self.ledger_amounts.get(
            Ledger.objects.get(ledger_kind=LedgerKind.VERKOOP_NIET_MARGE), 0
        ) + self.ledger_amounts.get(
            Ledger.objects.get(ledger_kind=LedgerKind.VERKOOP_MARGE), 0
        )

    @property
    def purchase_value(self):
        return (
            self.ledger_amounts.get(
                Ledger.objects.get(ledger_kind=LedgerKind.DIRECTE_AFSCHRIJVING), 0
            )
            + self.ledger_amounts.get(
                Ledger.objects.get(
                    ledger_kind=LedgerKind.VOORRAAD_BIJ_VERKOOP_NIET_MARGE
                ),
                0,
            )
            + self.ledger_amounts.get(
                Ledger.objects.get(ledger_kind=LedgerKind.VOORRAAD_BIJ_VERKOOP_MARGE), 0
            )
        )

    @property
    def is_sold(self):
        return (
            Ledger.objects.get(ledger_kind=LedgerKind.VERKOOP_MARGE)
            in self.ledger_amounts.keys()
            or Ledger.objects.get(ledger_kind=LedgerKind.VERKOOP_NIET_MARGE)
            in self.ledger_amounts.keys()
            and self.sales_value > 0
        )

    @property
    def is_amortized(self):
        if not self.collection.commerce:
            return None
        return self.stock_value == 0

    @property
    def is_amortized_not_at_purchase(self):
        return (
            Ledger.objects.get(ledger_kind=LedgerKind.AFSCHRIJVINGEN)
            in self.ledger_amounts.keys()
        )

    @property
    def is_amortized_at_purchase(self):
        return (
            Ledger.objects.get(ledger_kind=LedgerKind.DIRECTE_AFSCHRIJVING)
            in self.ledger_amounts.keys()
        )

    @property
    def is_margin(self):
        if not self.collection.commerce:
            return None
        return (
            Ledger.objects.get(ledger_kind=LedgerKind.VOORRAAD_MARGE)
            in self.ledger_amounts.keys()
        )

    @property
    def moneybird_status(self):
        if self.is_sold:
            return "Sold"
        if self.is_amortized and not self.is_amortized_at_purchase:
            return "Amortized"
        if self.is_amortized and self.is_amortized_at_purchase:
            return "Available or amortized"
        return "Available"

    def check_moneybird_errors(self):
        ledgers = self.ledger_amounts.keys()
        if self.is_margin and any(
            [
                Ledger.objects.get(ledger_kind=LedgerKind.VOORRAAD_NIET_MARGE)
                in ledgers,
                Ledger.objects.get(ledger_kind=LedgerKind.VERKOOP_NIET_MARGE)
                in ledgers,
                Ledger.objects.get(
                    ledger_kind=LedgerKind.VOORRAAD_BIJ_VERKOOP_NIET_MARGE
                )
                in ledgers,
            ]
        ):
            return "Margin asset on non-margin ledgers"

    def __str__(self):
        return f"{self.category.name_singular} {self.id} ({self.size})"


@receiver(models.signals.post_save, sender=Asset)
def on_asset_save(sender, instance: Asset, **kwargs):
    # pylint: disable=unused-argument
    """Link DocumentLines to their asset upon asset creation."""
    asset_id = instance.id
    document_lines = JournalDocumentLine.objects.filter(
        asset_id_field=asset_id
    ) + EstimateDocumentLine.objects.filter(asset_id_field=asset_id)
    for document_line in document_lines:
        document_line.asset = instance
        document_line.save()


def find_asset_id_from_description(description: str) -> Union[str, None]:
    match = re.search(r"\[\s*([\w\d]+)\s*\]", description)
    if match is None:
        return None
    return match.group(1)


def find_asset_from_id(asset_id) -> Union[Asset, None]:
    if asset_id is None:
        return None
    try:
        return Asset.objects.get(id=asset_id)
    except Asset.DoesNotExist:
        return None


@receiver(models.signals.pre_save, sender=JournalDocumentLine)
def on_document_line_save(sender, instance: JournalDocumentLine, **kwargs):
    # pylint: disable=unused-argument
    if instance.document.document_kind == DocumentKind.GENERAL_JOURNAL_DOCUMENT:
        description = instance.document.moneybird_json["reference"]
    else:
        description = instance.moneybird_json["description"]
    asset_id = find_asset_id_from_description(description)
    asset_or_none = find_asset_from_id(asset_id)
    instance.asset = asset_or_none
    instance.asset_id_field = asset_id


@receiver(models.signals.pre_save, sender=EstimateDocumentLine)
def on_document_line_save(sender, instance: EstimateDocumentLine, **kwargs):
    # pylint: disable=unused-argument
    description = instance.moneybird_json["description"]
    asset_id = find_asset_id_from_description(description)
    asset_or_none = find_asset_from_id(asset_id)
    instance.asset = asset_or_none
    instance.asset_id_field = asset_id


def attachments_directory_path(instance, filename):
    """Return the attachment's directory path."""
    return f"inventory/attachments/{instance.asset.id}/{filename}"


class Attachment(models.Model):
    """Class model for Attachments."""

    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, verbose_name=_("Asset"))
    attachment = models.FileField(
        upload_to=attachments_directory_path, verbose_name=_("Attachment")
    )
    upload_date = models.DateField(auto_now_add=True, verbose_name=_("Upload date"))
    remarks = models.TextField(verbose_name=_("Remarks"), max_length=1000, blank=True)

    def __str__(self):
        """Return Attachment string."""
        return f"{self.attachment} from {self.asset}"

    class Meta:
        """Meta Class to define verbose_name."""

        verbose_name = "Bijlage"

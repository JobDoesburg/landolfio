"""Asset models."""
from accounting.models import Invoice
from accounting.models import Receipt
from django.db import models
from django.utils.translation import gettext as _


STATES = (
    ("purchased", "purchased"),
    ("under_review", "under_review"),
    ("ready", "ready"),
    ("outgoing", "outgoing"),
    ("rented", "rented"),
    ("lent", "lent"),
    ("under_repair_internal", "under_repair_internal"),
    ("under_repair_external", "under_repair_external"),
    ("sold", "sold"),
    ("amoritzed", "amoritzed"),
)


class Asset(models.Model):
    """Class model for Assets."""

    old_id = models.CharField(verbose_name=_("Old ID"), max_length=200)
    # We may later add choices to the asset_type field, i.e. 'violin', 'cello' etc.
    # I named it `asset_type` instead of `type` because `type` shadows an existing function
    asset_type = models.CharField(verbose_name=_("Type"), max_length=200)
    # For the `size` field we may also want to add choices
    size = models.CharField(verbose_name=_("Size"), max_length=200)
    collection = models.CharField(verbose_name=_("Collection"), max_length=200)
    listing_price = models.FloatField(verbose_name=_("Listing price"))
    stock_price = models.FloatField(verbose_name=_("Stock price"))
    purchasing_value = models.FloatField(verbose_name=_("Stock price"))
    margin = models.BooleanField(verbose_name=_("Margin"))
    remarks = models.TextField(
        verbose_name=_("Remarks"), max_length=1000, null=True, blank=True
    )

    # Accounting related fields:
    receipt = models.ForeignKey(
        Receipt,
        on_delete=models.CASCADE,
        verbose_name=_("Receipt"),
        null=True,
        blank=True,
    )
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        verbose_name=_("Invoice"),
        null=True,
        blank=True,
    )

    class Meta:
        """Asset class meta data."""

        verbose_name = "Asset"
        verbose_name_plural = "Assets"

    def __str__(self):
        """Return Asset string."""
        # I think we should ask Job (client) how a string should be formed
        return str(self.asset_type) + " " + str(self.size)


class AssetState(models.Model):
    """Class model for Asset States."""

    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, verbose_name=_("Asset"))
    date = models.DateField(verbose_name=_("Date"))
    state = models.CharField(verbose_name=_("State"), choices=STATES, max_length=100)
    room = models.CharField(verbose_name=_("Room"), max_length=250)
    closet = models.CharField(verbose_name=_("Closet"), max_length=250)
    external = models.CharField(verbose_name=_("External"), max_length=250)

    class Meta:
        """AssetState class meta data."""

        verbose_name = "Asset state"
        verbose_name_plural = "Asset states"

    def __str__(self):
        """Return AssetState string."""
        return str(self.state) + " | " + str(self.state)

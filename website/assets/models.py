"""Asset models."""
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
    ("amortized", "amortized"),
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
    purchasing_value = models.FloatField(verbose_name=_("Purchasing value"))
    margin = models.BooleanField(verbose_name=_("Margin"))
    remarks = models.TextField(
        verbose_name=_("Remarks"), max_length=1000, null=True, blank=True
    )

    def __str__(self):
        """Return Asset string."""
        # I think we should ask Job (client) how a string should be formed
        return str(self.asset_type) + " " + str(self.size)


class AssetState(models.Model):
    """Class model for Asset States."""

    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, verbose_name=_("Asset"))
    date = models.DateField(verbose_name=_("Date"))
    state = models.CharField(verbose_name=_("State"), choices=STATES, max_length=100)
    room = models.CharField(
        verbose_name=_("Room"), max_length=250, null=True, blank=True
    )
    closet = models.CharField(
        verbose_name=_("Closet"), max_length=250, null=True, blank=True
    )
    external = models.CharField(
        verbose_name=_("External"), max_length=250, null=True, blank=True
    )

    def __str__(self):
        """Return AssetState string."""
        return str(self.state) + " | " + str(self.state)

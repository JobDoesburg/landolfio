"""Asset models."""
from django.db import models
from django.utils.translation import gettext as _


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

    def __str__(self):
        """Return Asset string."""
        return f"{self.name}"


class Asset(models.Model):
    """Class model for Assets."""

    id = models.CharField(verbose_name=_("ID"), max_length=200, primary_key=True)
    asset_type = models.CharField(verbose_name=_("Type"), max_length=200)
    size = models.CharField(verbose_name=_("Size"), max_length=200)
    collection = models.ForeignKey(
        Collection, on_delete=models.CASCADE, verbose_name=_("Collection")
    )
    listing_price = models.FloatField(verbose_name=_("Listing price"))
    stock_price = models.FloatField(verbose_name=_("Stock price"))
    purchasing_value = models.FloatField(verbose_name=_("Purchasing value"))
    remarks = models.TextField(
        verbose_name=_("Remarks"), max_length=1000, null=True, blank=True
    )
    MB_state = models.CharField(
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
    estimates = models.CharField(
        max_length=16, choices=Estimates, null=True, blank=True
    )

    def __str__(self):
        """Return Asset string."""
        return f"{self.asset_type} {self.size}"

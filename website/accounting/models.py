"""The accounting models."""
from assets.models import Asset
from django.db import models
from django.utils.translation import gettext as _


class Invoice(models.Model):
    """Class model for Invoices."""

    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, verbose_name=_("Asset"))
    json_MB = models.JSONField(verbose_name=_("JSON MoneyBird"))
    date = models.DateField(verbose_name=_("Date"))
    amount = models.FloatField(verbose_name=_("Amount"))

    # pylint: disable=no-member
    def __str__(self):
        """Return Invoice string."""
        return "IV_" + str(self.date) + "_" + str(self.id)


class Receipt(models.Model):
    """Class model for Receipts."""

    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, verbose_name=_("Asset"))
    json_MB = models.JSONField(verbose_name=_("JSON MoneyBird"))
    date = models.DateField(verbose_name=_("Date"))
    amount = models.FloatField(verbose_name=_("Amount"))

    # pylint: disable=no-member
    def __str__(self):
        """Return Receipt string."""
        return "RC_" + str(self.date) + "_" + str(self.id)
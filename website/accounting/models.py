from django.db import models
from django.utils.translation import gettext as _


class Invoice(models.Model):
    """Class model for Invoices."""

    json_MB = models.JSONField(verbose_name=_("JSON MoneyBird"))
    date = models.DateField(verbose_name=_("Date"))
    amount = models.FloatField(verbose_name=_("Amount"))

    class Meta:
        """Invoice class meta data."""

        verbose_name = "Invoice"
        verbose_name_plural = "Invoices"

    def __str__(self):
        """Return Invoice string."""
        # Wat is een logische string hier?
        return "Invoice " + str(self.date)


class Receipt(models.Model):
    """Class model for Receipts."""

    json_MB = models.JSONField(verbose_name=_("JSON MoneyBird"))
    date = models.DateField(verbose_name=_("Date"))
    amount = models.FloatField(verbose_name=_("Amount"))

    class Meta:
        """Receipt class meta data."""

        verbose_name = "Receipt"
        verbose_name_plural = "Receipts"

    def __str__(self):
        """Return Receipt string."""
        # Wat is een logische string hier?
        return "Receipt " + str(self.date)

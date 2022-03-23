from assets.models import Asset
from django.db import models
from django.utils.translation import gettext as _


class DocumentLine(models.Model):
    json_MB = models.JSONField(verbose_name=_("JSON MoneyBird"))
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, verbose_name=_("Asset"))
    price = models.FloatField(verbose_name=_("Price"))


class Document(models.Model):
    """Class model for Documents."""

    class Kind(models.TextChoices):
        """The kind of document."""

        INVOICE = "IV", _("Invoice")
        RECEIPT = "RC", _("Receipt")

    json_MB = models.JSONField(verbose_name=_("JSON MoneyBird"))
    kind = models.CharField(max_length=2, choices=Kind.choices)
    date = models.DateField(verbose_name=_("Date"))
    lines = models.ManyToManyField(DocumentLine)

    def __str__(self):
        """Return Document string."""
        # pylint: disable=no-member
        return f"{str(self.kind)}_{str(self.date)}_{str(self.id)}"

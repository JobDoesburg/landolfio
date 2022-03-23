from django.db import models
from django.utils.translation import gettext as _


class Document(models.Model):
    """Class model for Documents."""

    class Kind(models.TextChoices):
        """The kind of document."""

        PURCHASE_INVOICE = "PI", _("Purchase Invoice")
        RECEIPT = "RC", _("Receipt")

    json_MB = models.JSONField(verbose_name=_("JSON MoneyBird"))
    kind = models.CharField(max_length=2, choices=Kind.choices)

    def __str__(self):
        """Return Document string."""
        # pylint: disable=no-member
        return f"{str(self.kind)}_{str(self.id)}"

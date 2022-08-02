from django.db import models
from django.utils.translation import gettext_lazy as _


class AssetStates(models.TextChoices):
    UNKNOWN = "unknown", _("unknown")
    PLACEHOLDER = "placeholder", _("placeholder")
    TO_BE_DELIVERED = "to_be_delivered", _("to be delivered")
    UNDER_REVIEW = "under_review", _("under review")
    MAINTENANCE_IN_HOUSE = "maintenance_in_house", _("maintenance in house")
    MAINTENANCE_EXTERNAL = "maintenance_external", _("maintenance external")
    AVAILABLE = "available", _("available")
    ISSUED_UNPROCESSED = "issued_unprocessed", _("issued unprocessed")
    ISSUED_RENT = "issued_rent", _("issued rent")
    ISSUED_LOAN = "issued_loan", _("issued loan")
    AMORTIZED = "amortized", _("amortized")
    SOLD = "sold", _("sold")

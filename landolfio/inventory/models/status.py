from django.db import models
from django.utils.translation import gettext_lazy as _


class AssetStates(models.TextChoices):
    UNKNOWN = "unknown", _("Unknown")
    PLACEHOLDER = "placeholder", _("Placeholder")
    TO_BE_DELIVERED = "to_be_delivered", _("To be delivered")
    UNDER_REVIEW = "under_review", _("Under review")
    MAINTENANCE_IN_HOUSE = "maintenance_in_house", _("Maintenance in house")
    MAINTENANCE_EXTERNAL = "maintenance_external", _("Maintenance external")
    AVAILABLE = "available", _("Available")
    ISSUED_UNPROCESSED = "issued_unprocessed", _("Issued unprocessed")
    ISSUED_RENT = "issued_rent", _("Issued rent")
    ISSUED_LOAN = "issued_loan", _("Issued loan")
    AMORTIZED = "amortized", _("Amortized")
    SOLD = "sold", _("Sold")

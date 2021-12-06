from django.core.exceptions import ValidationError
from django.core.validators import validate_unicode_slug
from django.db import models
from django.db.models import PROTECT

from assets.models.asset_location import AssetLocation


class AssetCategory(models.Model):
    class Meta:
        verbose_name = "category"
        verbose_name_plural = "categories"

    name = models.CharField(null=False, blank=False, max_length=20)
    name_singular = models.CharField(null=False, blank=False, max_length=20, validators=[validate_unicode_slug])

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


class Asset(models.Model):
    class Meta:
        verbose_name = "asset"
        verbose_name_plural = "assets"

    UNKNOWN = 0
    PLACEHOLDER = 1
    TO_BE_DELIVERED = 2
    UNDER_REVIEW = 3
    MAINTENANCE_IN_HOUSE = 4
    MAINTENANCE_EXTERNAL = 5
    AVAILABLE = 6
    ISSUED_UNPROCESSED = 7
    ISSUED_RENT = 8
    ISSUED_LOAN = 9
    AMORTIZED = 10
    SOLD = 11

    STATUS_CHOICES = (
        (UNKNOWN, "Unknown"),
        (PLACEHOLDER, "Placeholder reserved"),
        (TO_BE_DELIVERED, "To be delivered"),
        (UNDER_REVIEW, "Under review"),
        (MAINTENANCE_IN_HOUSE, "Maintenance (in house)"),
        (MAINTENANCE_EXTERNAL, "Maintenance (external)"),
        (AVAILABLE, "Available"),
        (ISSUED_UNPROCESSED, "Issued (unprocessed)"),
        (ISSUED_RENT, "Issued (rental)"),
        (ISSUED_LOAN, "Issued (loan)"),
        (AMORTIZED, "Amortized"),
        (SOLD, "Sold"),
    )

    BUSINESS = 0
    PRIVATE = 1
    CONSIGNMENT = 2

    COLLECTION_CHOICES = (
        (BUSINESS, "Business"),
        (PRIVATE, "Private"),
        (CONSIGNMENT, "Consignment"),
    )

    MARGIN = 0
    TAXABLE = 1

    TAX_STATUS_CHOICES = (
        (MARGIN, "Margin"),
        (TAXABLE, "Taxable"),
    )

    number = models.CharField(null=False, blank=False, unique=True, max_length=10, primary_key=True, validators=[validate_unicode_slug])
    category = models.ForeignKey(AssetCategory, null=False, blank=False, on_delete=PROTECT)
    size = models.ForeignKey(AssetSize, null=True, blank=True, on_delete=PROTECT)

    status = models.IntegerField(null=False, blank=False, choices=STATUS_CHOICES, default=PLACEHOLDER)
    location = models.ForeignKey(
        AssetLocation, null=True, blank=True, on_delete=PROTECT
    )

    collection = models.IntegerField(null=False, blank=False, choices=COLLECTION_CHOICES, default=BUSINESS)

    tax_status = models.IntegerField(null=False, blank=False, choices=TAX_STATUS_CHOICES, default=TAXABLE)

    retail_value = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2)

    remarks = models.TextField(null=True, blank=True)

    def clean(self):
        super().clean()
        errors = {}

        if self.collection == self.PRIVATE and self.tax_status != self.MARGIN:
            errors.update(
                {
                    "tax_status": f"Private assets are margin by default"
                }
            )

        try:
            size = self.size
            if size:
                if self.category not in size.categories.all():
                    errors.update(
                        {
                            "size": f"This size does not match the category of this asset. Choices are: {', '.join(self.category.assetsize_set.values_list('name', flat=True))}."
                        }
                    )
        except AssetCategory.DoesNotExist:
            pass

        if errors:
            raise ValidationError(errors)

    @property
    def current_stock_value(self):
        """
        For what amount can this asset be found on the stock balance ledger right now?
        This is the sum of all bookings to the stock balance ledger for this asset
        - 0 if it has no purchase documents at all
        - 0 if it has been sold or amortized
        - 0 if it has been (fiscally) amortized directly after sales
        """
        return None

    @property
    def purchase_value(self):
        """
        This is the sum of all POSITIVE bookings to the stock balance ledger for this asset,
        or the sum of all bookings to the fiscal amortization ledger for this asset.
        """
        return None

    @property
    def sales_value(self):
        """
        This is the sum of all POSITIVE bookings to the stock balance ledger for this asset,
        """
        return None

    def check_stock_balance_ledger_integrity(self):
        """
        Perform some integrity checks
        """
        raise NotImplementedError

    def __str__(self):
        return f"{self.category.name_singular} {self.number}"

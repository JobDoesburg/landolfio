from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import PROTECT

from assets.models.asset_location import AssetLocation


class AssetCategory(models.Model):
    class Meta:
        verbose_name = "category"
        verbose_name_plural = "categories"

    name = models.CharField(null=False, blank=False, max_length=20)
    name_singular = models.CharField(null=False, blank=False, max_length=20)

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
        unique_together = ["number", "category"]

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

    number = models.CharField(null=False, blank=False, max_length=10)
    category = models.ForeignKey(AssetCategory, null=False, blank=False, on_delete=PROTECT)
    size = models.ForeignKey(AssetSize, null=True, blank=True, on_delete=PROTECT)

    status = models.IntegerField(null=False, blank=False, choices=STATUS_CHOICES, default=PLACEHOLDER)
    location = models.ForeignKey(
        AssetLocation, null=True, blank=True, on_delete=PROTECT
    )  # constraint, cannot be null if available, etc... write on review (suggest previous)

    retail_value = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2)

    def clean(self):
        super().clean()
        errors = {}
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

    def get_last_event(self):
        return self.event_set.all().last()

    @property
    def stock_value(self):
        raise NotImplementedError  # return the sum of the purchase documents

    @property
    def purchase_documents(self):
        raise NotImplementedError  # return all documents with an invoice row to this asset with a positive result on a stock ledger

    @property
    def collection(self):
        raise NotImplementedError  # return some collection (maybe derive it from purchase documents, maybe make a new foreignkey choice field)

    @property
    def tax_status(self):
        raise NotImplementedError  # Return "margin good" or "taxable good"

    def get_status(self):
        return self.STATUS_CHOICES[self.status][1]

    def __str__(self):
        return f"{self.number} ({self.category.name_singular})"

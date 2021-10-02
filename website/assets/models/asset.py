from django.core.exceptions import ValidationError
from django.core.validators import validate_unicode_slug
from django.db import models
from django.db.models import PROTECT
from model_utils import FieldTracker

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

    number = models.CharField(null=False, blank=False, unique=True, max_length=10, primary_key=True, validators=[validate_unicode_slug])
    category = models.ForeignKey(AssetCategory, null=False, blank=False, on_delete=PROTECT)
    size = models.ForeignKey(AssetSize, null=True, blank=True, on_delete=PROTECT)

    status = models.IntegerField(null=False, blank=False, choices=STATUS_CHOICES, default=PLACEHOLDER)
    location = models.ForeignKey(
        AssetLocation, null=True, blank=True, on_delete=PROTECT
    )  # constraint, cannot be null if available, etc... write on review (suggest previous)

    retail_value = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2)

    tracker = FieldTracker(['number', 'category', 'size', 'status'])

    def get_immutable_fields(self):
        immutable_fields = []
        if getattr(self, 'number') is not None:
            immutable_fields.append('number')
        if getattr(self, 'category') is not None:
            immutable_fields.append('category')
        if getattr(self, 'size') is not None:
            immutable_fields.append('size')
        return immutable_fields

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        for field in self.get_immutable_fields():
            if self.tracker.has_changed(field) and (self.tracker.previous('field') is not None):
                raise ValidationError("This field is immutable.")
        super().save(force_insert, force_update, using, update_fields)

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

    def get_event_history(self):
        return sorted(self.event_set.all(), key=lambda e: e.date)

    def get_last_event(self):
        return self.get_event_history()[-1] if self.get_event_history() else None

    @property
    def stock_value(self):
        raise NotImplementedError  # return the sum of the purchase documents

    @property
    def purchase_documents(self):
        from purchases.models import SingleAssetPurchase
        return sorted(self.event_set.all().instance_of(SingleAssetPurchase), key=lambda e: e.date)  # TODO add documents

    @property
    def collection(self):
        raise NotImplementedError  # return some collection (maybe derive it from purchase documents, maybe make a new foreignkey choice field)

    @property
    def tax_status(self):
        raise NotImplementedError  # Return "margin good" or "taxable good"

    def get_status(self):
        return self.STATUS_CHOICES[self.status][1]

    def __str__(self):
        return f"{self.category.name_singular} {self.number}"

# TODO add collection
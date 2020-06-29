from django.db import models
from django.db.models import PROTECT, CASCADE


class AssetType(models.Model):
    class Meta:
        verbose_name = "type"
        verbose_name_plural = "types"

    name = models.CharField(null=False, blank=False, max_length=20)

    def __str__(self):
        return f"{self.name}"


class Asset(models.Model):
    class Meta:
        verbose_name = "asset"
        verbose_name_plural = "assets"
        unique_together = ['number', 'category']

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
        (UNKNOWN, 'Unknown'),
        (PLACEHOLDER, 'Placeholder reserved'),
        (TO_BE_DELIVERED, 'To be delivered'),
        (UNDER_REVIEW, 'Under review'),
        (MAINTENANCE_IN_HOUSE, 'Maintenance (in house)'),
        (MAINTENANCE_EXTERNAL, 'Maintenance (external)'),
        (AVAILABLE, 'Available'),
        (ISSUED_UNPROCESSED, 'Issued (unprocessed)'),
        (ISSUED_RENT, 'Issued (rental)'),
        (ISSUED_LOAN, 'Issued (loan)'),
        (AMORTIZED, 'Amortized'),
        (SOLD, 'Sold'),
    )

    number = models.CharField(null=False, blank=False, max_length=10)
    category = models.ForeignKey(AssetType, null=False, blank=False, on_delete=PROTECT)
    status = models.IntegerField(null=False, blank=False, choices=STATUS_CHOICES, default=PLACEHOLDER)

    def __str__(self):
        return f"{self.category} {self.number}"


class AssetMemo(models.Model):
    class Meta:
        verbose_name = "memo"
        verbose_name_plural = "memos"

    created = models.DateTimeField(auto_created=True, blank=False, null=False)
    instrument = models.ForeignKey(Asset, null=False, blank=False, on_delete=CASCADE)
    memo = models.TextField(null=False, blank=False)

    def __str__(self):
        return f"Memo {self.created}: {self.instrument}"


class AssetEvent(models.Model):
    class Meta:
        verbose_name = "event"
        verbose_name_plural = "events"

    START_RENT = 0
    EVENT_TYPES = (
        (START_RENT, 'Rental start'),
    )

    created = models.DateTimeField(auto_created=True, blank=False, null=False)
    event_date = models.DateTimeField(blank=False, null=False)
    instrument = models.ForeignKey(Asset, null=False, blank=False, on_delete=PROTECT)
    type = models.IntegerField(null=False, blank=False, choices=EVENT_TYPES)

    def __str__(self):
        return f"{self.type} ({self.event_date}): {self.instrument}"


class AssetLocation(models.Model):
    class Meta:
        verbose_name = "location"
        verbose_name_plural = "events"

    START_RENT = 0
    EVENT_TYPES = (
        (START_RENT, 'Rental start'),
    )

    created = models.DateTimeField(auto_created=True, blank=False, null=False)
    event_date = models.DateTimeField(blank=False, null=False)
    instrument = models.ForeignKey(Asset, null=False, blank=False, on_delete=PROTECT)
    type = models.IntegerField(null=False, blank=False, choices=EVENT_TYPES)

    def __str__(self):
        return f"{self.type} ({self.event_date}): {self.instrument}"


class RentedOut(AssetEvent):
    input_statuses = [Asset.AVAILABLE, Asset.ISSUED_UNPROCESSED]
    output_status = Asset.ISSUED_RENT


class Loaned(AssetEvent):
    input_statuses = [Asset.AVAILABLE, Asset.ISSUED_UNPROCESSED]
    output_status = Asset.ISSUED_RENT


class PlaceholderRegistered:
    input_statuses = None
    output_status = Asset.PLACEHOLDER


class PurchasedNotDelivered(AssetEvent):
    input_statuses = [None, Asset.PLACEHOLDER]
    output_status = Asset.TO_BE_DELIVERED


class Delivered(AssetEvent):
    input_statuses = [Asset.TO_BE_DELIVERED]
    output_status = Asset.UNDER_REVIEW


class PurchasedAndDelivered(AssetEvent):
    input_statuses = [None, Asset.PLACEHOLDER]
    output_status = Asset.UNDER_REVIEW


class NeedsMaintenance(AssetEvent):
    input_statuses = [Asset.UNDER_REVIEW, Asset.PLACEHOLDER]
    output_status = Asset.MAINTENANCE_IN_HOUSE


class Sold(AssetEvent):
    input_statuses = [Asset.AVAILABLE, Asset.ISSUED_UNPROCESSED, Asset.ISSUED_RENT, Asset.ISSUED_LOAN]
    output_status = Asset.SOLD


class Amortized(AssetEvent):
    input_statuses = [Asset.AVAILABLE, Asset.UNDER_REVIEW,
                      Asset.MAINTENANCE_IN_HOUSE, Asset.MAINTENANCE_EXTERNAL, Asset.ISSUED_LOAN, Asset.ISSUED_RENT, Asset.ISSUED_UNPROCESSED]
    output_status = Asset.AMORTIZED


class MadeAvailable(AssetEvent):
    input_statuses = [Asset.UNDER_REVIEW, Asset.MAINTENANCE_IN_HOUSE, Asset.MAINTENANCE_EXTERNAL]
    output_status = Asset.AVAILABLE


class Returned(AssetEvent):
    input_statuses = [Asset.ISSUED_UNPROCESSED, Asset.ISSUED_RENT, Asset.ISSUED_LOAN]
    output_status = Asset.UNDER_REVIEW


class LostTrack(AssetEvent):
    input_statuses = [Asset.TO_BE_DELIVERED, Asset.UNDER_REVIEW, Asset.MAINTENANCE_IN_HOUSE, Asset.MAINTENANCE_EXTERNAL, Asset.AVAILABLE, Asset.ISSUED_UNPROCESSED, Asset.ISSUED_RENT, Asset.ISSUED_LOAN]
    output_status = Asset.UNDER_REVIEW


class ReturnedFromUnknown(AssetEvent):
    input_status = Asset.UNKNOWN
    output_statuses = Asset.STATUS_CHOICES



class FinancialActions:

    @staticmethod
    def put_on_stock_ledger(asset, bought_from_ledger):
        pass

    @staticmethod
    def take_off_stock_ledger(asset, sold_to_ledger):
        pass


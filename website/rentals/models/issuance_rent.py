from django.db import models
from django.db.models import PROTECT

from asset_events.models import StatusChangingEvent, MultiAssetEvent
from assets.models import Asset
from moneybird_accounting.models import Contact


class SingleAssetRental(StatusChangingEvent):
    class Meta:
        verbose_name = "asset rental"
        verbose_name_plural = "asset rentals"

    input_statuses = [Asset.AVAILABLE, Asset.ISSUED_UNPROCESSED]
    output_status = Asset.ISSUED_RENT

    rental = models.ForeignKey("AssetRental", null=False, blank=False, on_delete=PROTECT)

    @property
    def contact(self):
        return self.sale.contact

    def date(self):
        return self.sale.date


class AssetRental(MultiAssetEvent):
    class Meta:
        verbose_name = "rental"
        verbose_name_plural = "rentals"

    contact = models.ForeignKey(Contact, null=True, blank=True, on_delete=PROTECT)
    assets = models.ManyToManyField(Asset, through=SingleAssetRental)

    def __str__(self):
        return f"Rental {', '.join(self.assets.values_list('number', flat=True))}"

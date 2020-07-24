from django.db import models
from django.db.models import PROTECT

from asset_events.models import StatusChangingEvent, MultiAssetEvent
from assets.models import Asset


class SingleAssetDelivery(StatusChangingEvent):
    class Meta:
        verbose_name = "asset delivery"
        verbose_name_plural = "asset deliveries"

    input_statuses = [Asset.TO_BE_DELIVERED]
    output_status = Asset.UNDER_REVIEW

    delivery = models.ForeignKey("AssetDelivery", null=False, blank=False, on_delete=PROTECT)

    @property
    def contact(self):
        return self.sale.contact

    def date(self):
        return self.sale.date

    # todo sync with MB to right results ledger


class AssetDelivery(MultiAssetEvent):
    class Meta:
        verbose_name = "delivery"
        verbose_name_plural = "deliveries"

    assets = models.ManyToManyField(Asset, through=SingleAssetDelivery)

    def __str__(self):
        return f"Delivery {self.date}"

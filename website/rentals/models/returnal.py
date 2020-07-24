from django.db import models
from django.db.models import PROTECT

from asset_events.models import StatusChangingEvent, MultiAssetEvent
from assets.models import Asset


class SingleAssetReturnal(StatusChangingEvent):
    class Meta:
        verbose_name = "asset returnal"
        verbose_name_plural = "asset returnals"

    input_statuses = [Asset.ISSUED_RENT, Asset.ISSUED_LOAN, Asset.ISSUED_UNPROCESSED]
    output_status = Asset.UNDER_REVIEW

    returnal = models.ForeignKey("AssetReturnal", null=False, blank=False, on_delete=PROTECT)

    @property
    def contact(self):
        return self.sale.contact

    def date(self):
        return self.sale.date


class AssetReturnal(MultiAssetEvent):
    class Meta:
        verbose_name = "returnal"
        verbose_name_plural = "returnals"

    assets = models.ManyToManyField(Asset, through=SingleAssetReturnal)

    def __str__(self):
        return f"Returnal {self.date}"

from django.db import models
from django.db.models import PROTECT

from asset_events.models import StatusChangingEvent, MultiAssetEvent
from assets.models import Asset
from moneybird_accounting.models import Contact


class SingleUnprocessedAssetIssuance(StatusChangingEvent):
    class Meta:
        verbose_name = "unprocessed asset issuance"
        verbose_name_plural = "unprocessed asset issuances"

    input_statuses = [Asset.AVAILABLE, Asset.ISSUED_UNPROCESSED]
    output_status = Asset.ISSUED_UNPROCESSED

    issuance = models.ForeignKey("UnprocessedAssetIssuance", null=False, blank=False, on_delete=PROTECT)

    @property
    def contact(self):
        return self.sale.contact

    def date(self):
        return self.sale.date


class UnprocessedAssetIssuance(MultiAssetEvent):
    class Meta:
        verbose_name = "unprocessed issuance"
        verbose_name_plural = "unprocessed issuances"

    contact = models.ForeignKey(Contact, null=True, blank=True, on_delete=PROTECT)
    assets = models.ManyToManyField(Asset, through=SingleUnprocessedAssetIssuance)

    def __str__(self):
        return f"Issuance {', '.join(self.assets.values_list('number', flat=True))}"

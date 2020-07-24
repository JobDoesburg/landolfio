from django.db import models
from django.db.models import PROTECT

from asset_events.models import StatusChangingEvent, MultiAssetEvent
from assets.models import Asset
from moneybird_accounting.models import Contact


class SingleAssetSale(StatusChangingEvent):
    class Meta:
        verbose_name = "asset sale"
        verbose_name_plural = "asset sales"

    input_statuses = [Asset.AVAILABLE, Asset.ISSUED_UNPROCESSED, Asset.ISSUED_RENT, Asset.ISSUED_LOAN]
    output_status = Asset.SOLD

    sale = models.ForeignKey("AssetSale", null=False, blank=False, on_delete=PROTECT)

    @property
    def contact(self):
        return self.sale.contact

    def date(self):
        return self.sale.date

    # todo sync with MB to right results ledger


class AssetSale(MultiAssetEvent):
    class Meta:
        verbose_name = "sale"
        verbose_name_plural = "sales"

    contact = models.ForeignKey(Contact, null=True, blank=True, on_delete=PROTECT)
    assets = models.ManyToManyField(Asset, through=SingleAssetSale)

    def __str__(self):
        return f"Sale {', '.join(self.assets.values_list('number', flat=True))}"


# TODO add Inkoop of already saled instrument, ruilconstructies

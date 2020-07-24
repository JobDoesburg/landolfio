from django.db import models
from django.db.models import PROTECT

from asset_events.models import StatusChangingEvent, MultiAssetEvent
from assets.models import Asset
from moneybird_accounting.models import Contact


class SingleAssetPurchase(StatusChangingEvent):
    class Meta:
        verbose_name = "asset purchase"
        verbose_name_plural = "asset purchases"

    input_statuses = [Asset.PLACEHOLDER]

    def get_output_status(self):
        return Asset.UNDER_REVIEW if self.already_delivered else Asset.TO_BE_DELIVERED

    already_delivered = models.BooleanField(default=False, null=False, blank=False)
    purchase = models.ForeignKey("AssetPurchase", null=False, blank=False, on_delete=PROTECT)

    @property
    def contact(self):
        return self.sale.contact

    def date(self):
        return self.sale.date

    # todo sync with MB to right results ledger


class AssetPurchase(MultiAssetEvent):
    class Meta:
        verbose_name = "purchase"
        verbose_name_plural = "purchases"

    contact = models.ForeignKey(Contact, null=True, blank=True, on_delete=PROTECT)
    assets = models.ManyToManyField(Asset, through=SingleAssetPurchase)

    def __str__(self):
        return f"Purchase {self.date}"

    # TODO add FK to purchaseinvoiceitem (tax status and net. price), add collection field, sync with MB to right stock ledger

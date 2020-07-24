from django.db import models
from django.db.models import PROTECT

from asset_events.models import StatusChangingEvent, MultiAssetEvent
from assets.models import Asset
from moneybird_accounting.models import Contact


class SingleAssetLoan(StatusChangingEvent):
    class Meta:
        verbose_name = "asset loan"
        verbose_name_plural = "asset loans"

    input_statuses = [Asset.AVAILABLE, Asset.ISSUED_UNPROCESSED]
    output_status = Asset.ISSUED_LOAN

    loan = models.ForeignKey("AssetLoan", null=False, blank=False, on_delete=PROTECT)

    @property
    def contact(self):
        return self.sale.contact

    def date(self):
        return self.sale.date


class AssetLoan(MultiAssetEvent):
    class Meta:
        verbose_name = "loan"
        verbose_name_plural = "loans"

    contact = models.ForeignKey(Contact, null=True, blank=True, on_delete=PROTECT)
    assets = models.ManyToManyField(Asset, through=SingleAssetLoan)

    def __str__(self):
        return f"Loan {', '.join(self.assets.values_list('number', flat=True))}"

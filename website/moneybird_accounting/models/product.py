from django.db import models
from django.db.models import PROTECT

from moneybird_accounting.models import MoneybirdReadWriteResourceModel
from moneybird_accounting.models.ledger_account import LedgerAccount
from moneybird_accounting.models.tax_rate import TaxRate


class Product(MoneybirdReadWriteResourceModel):
    class Meta:
        verbose_name = "product"
        verbose_name_plural = "products"

    moneybird_resource_path_name = "products"
    moneybird_resource_name = "product"

    moneybird_data_fields = [
        "description",
        "price",
        "tax_rate_id",
        "ledger_account_id",
    ]  # TODO add frequency_type

    description = models.CharField(blank=True, null=True, max_length=1000)
    price = models.DecimalField(blank=True, null=True, max_digits=10, decimal_places=2)
    tax_rate = models.ForeignKey(TaxRate, blank=True, null=True, on_delete=PROTECT, db_constraint=False)
    ledger_account = models.ForeignKey(LedgerAccount, blank=True, null=True, on_delete=PROTECT, db_constraint=False)

    def __str__(self):
        return self.description

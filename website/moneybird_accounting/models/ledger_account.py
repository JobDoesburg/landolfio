from django.db import models
from django.db.models import PROTECT

from moneybird_accounting.models import MoneybirdReadWriteResourceModel


class LedgerAccount(MoneybirdReadWriteResourceModel):
    class Meta:
        verbose_name = "ledger account"
        verbose_name_plural = "ledger accounts"

    moneybird_resource_path_name = "ledger_accounts"
    moneybird_resource_name = "ledger_account"

    moneybird_data_fields = [
        "name",
        "account_type",
        "account_id",
        "parent_id",
    ]  # TODO add allowed_document_types and limit foreign key choices

    name = models.CharField(blank=True, null=True, max_length=100)

    ACCOUNT_TYPE_NON_CURRENT_ASSETS = "non_current_assets"
    ACCOUNT_TYPE_CURRENT_ASSETS = "current_assets"
    ACCOUNT_TYPE_EQUITY = "equity"
    ACCOUNT_TYPE_PROVISIONS = "provisions"
    ACCOUNT_TYPE_NON_CURRENT_LIABILITIES = "non_current_liabilities"
    ACCOUNT_TYPE_CURRENT_LIABILITIES = "current_liabilities"
    ACCOUNT_TYPE_REVENUE = "revenue"
    ACCOUNT_TYPE_DIRECT_COSTS = "direct_costs"
    ACCOUNT_TYPE_EXPENSES = "expenses"
    ACCOUNT_TYPE_OTHER_INCOME_EXPENSES = "other_income_expenses"
    ACCOUNT_TYPE_CHOICES = (
        (ACCOUNT_TYPE_NON_CURRENT_ASSETS, "Non-current assets"),
        (ACCOUNT_TYPE_CURRENT_ASSETS, "Currents assets"),
        (ACCOUNT_TYPE_EQUITY, "Equity"),
        (ACCOUNT_TYPE_PROVISIONS, "Provisions"),
        (ACCOUNT_TYPE_NON_CURRENT_LIABILITIES, "Non-current liabilities"),
        (ACCOUNT_TYPE_CURRENT_LIABILITIES, "Current liabilities"),
        (ACCOUNT_TYPE_REVENUE, "Revenue"),
        (ACCOUNT_TYPE_DIRECT_COSTS, "Direct costs"),
        (ACCOUNT_TYPE_EXPENSES, "Expenses"),
        (ACCOUNT_TYPE_OTHER_INCOME_EXPENSES, "Other income or expenses"),
    )

    account_type = models.CharField(blank=True, null=True, choices=ACCOUNT_TYPE_CHOICES, max_length=50)
    account_id = models.CharField(blank=True, null=True, max_length=10)
    parent = models.ForeignKey("LedgerAccount", blank=True, null=True, on_delete=PROTECT, db_constraint=False)

    def __str__(self):
        return self.name

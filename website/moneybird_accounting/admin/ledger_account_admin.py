from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from moneybird_accounting.models.ledger_account import LedgerAccount


@admin.register(LedgerAccount)
class MoneybirdLedgerAccountAdmin(ImportExportModelAdmin):
    pass

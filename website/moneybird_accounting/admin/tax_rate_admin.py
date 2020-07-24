from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from moneybird_accounting.models.tax_rate import TaxRate


@admin.register(TaxRate)
class MoneybirdTaxRateAdmin(ImportExportModelAdmin):
    pass

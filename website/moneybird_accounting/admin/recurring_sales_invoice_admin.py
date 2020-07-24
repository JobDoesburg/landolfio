from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from moneybird_accounting.models.recurring_sales_invoice import RecurringSalesInvoice


@admin.register(RecurringSalesInvoice)
class MoneybirdRecurringSalesInvoiceAdmin(ImportExportModelAdmin):
    pass
    # TODO fix this admin

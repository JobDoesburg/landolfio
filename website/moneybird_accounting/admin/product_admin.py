from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from moneybird_accounting.models.product import Product


@admin.register(Product)
class MoneybirdProductAdmin(ImportExportModelAdmin):
    pass

from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from moneybird_accounting.models import Workflow


@admin.register(Workflow)
class MoneybirdWorkflowAdmin(ImportExportModelAdmin):
    pass

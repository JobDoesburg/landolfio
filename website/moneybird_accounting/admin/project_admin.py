from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from moneybird_accounting.models.project import Project


@admin.register(Project)
class MoneybirdProductAdmin(ImportExportModelAdmin):
    pass

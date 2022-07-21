from django.contrib.admin import register

from accounting.models.project import Project
from moneybird.admin import MoneybirdResourceModelAdmin


@register(Project)
class ProjectAdmin(MoneybirdResourceModelAdmin):
    ordering = ("-active", "name",)
    list_display = (
        "name",
        "active",
        "moneybird_id",
    )
    list_filter = ("active",)

    search_fields = ("name",)

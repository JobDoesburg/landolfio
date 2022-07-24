from django.contrib.admin import register

from accounting.models.workflow import Workflow
from moneybird.admin import MoneybirdResourceModelAdmin


@register(Workflow)
class WorkflowAdmin(MoneybirdResourceModelAdmin):
    ordering = ("name",)
    list_display = (
        "name",
        "type",
        "active",
    )
    list_filter = ("type", "active")
    search_fields = (
        "name",
        "type",
    )

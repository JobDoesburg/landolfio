from django.contrib.admin import register

from accounting.models.document_style import DocumentStyle
from moneybird.admin import MoneybirdResourceModelAdmin


@register(DocumentStyle)
class DocumentStyleAdmin(MoneybirdResourceModelAdmin):
    ordering = (
        "-default",
        "name",
    )
    list_display = (
        "name",
        "default",
        "view_on_moneybird",
        "_synced_with_moneybird",
    )
    search_fields = ("name",)

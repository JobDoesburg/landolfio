from autocompletefilter.admin import AutocompleteFilterMixin
from autocompletefilter.filters import AutocompleteListFilter
from django.contrib import admin
from django.contrib.admin import register

from accounting.models import GeneralJournalDocument, GeneralJournalDocumentLine
from moneybird.admin import (
    MoneybirdResourceModelAdmin,
    MoneybirdResourceModelForm,
    MoneybirdResourceModelFormSet,
)


class GeneralJournalDocumentLineInline(admin.StackedInline):
    """The admin view for DocumentLines."""

    model = GeneralJournalDocumentLine
    fields = (
        "ledger_account",
        "debit",
        "credit",
        "total_amount",
        "project",
        "description",
        "row_order",
    )
    readonly_fields = ["total_amount"]
    extra = 0
    autocomplete_fields = ["ledger_account", "project", "asset"]
    min_num = 2
    #
    # form = MoneybirdResourceModelForm
    # formset = MoneybirdResourceModelFormSet
    # TODO fix this


@register(GeneralJournalDocument)
class GeneralJournalDocumentAdmin(AutocompleteFilterMixin, MoneybirdResourceModelAdmin):
    ordering = ("-date", "reference")
    list_display = (
        "__str__",
        "date",
        "view_on_moneybird",
    )
    date_hierarchy = "date"
    list_filter = (("document_lines__ledger_account", AutocompleteListFilter),)

    search_fields = ("reference",)
    inlines = (GeneralJournalDocumentLineInline,)

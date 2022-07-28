import datetime
from decimal import Decimal

from django.db import models
from django.utils.translation import gettext as _

from accounting.models.contact import Contact, ContactResourceType
from accounting.models.journal_document import (
    JournalDocumentLine,
    JournalDocumentResourceType,
)
from moneybird import resources
from moneybird.models import (
    SynchronizableMoneybirdResourceModel,
)
from moneybird.resource_types import MoneybirdResource


class GeneralJournalDocument(SynchronizableMoneybirdResourceModel):
    date = models.DateField(null=True, blank=True, verbose_name=_("date"))
    reference = models.CharField(
        max_length=255, null=True, blank=True, verbose_name=_("reference")
    )

    def __str__(self):
        return self.reference


class GeneralJournalDocumentLine(JournalDocumentLine):
    document = models.ForeignKey(
        GeneralJournalDocument,
        on_delete=models.CASCADE,
        verbose_name=_("Document"),
        related_name="document_lines",
    )

    contact = models.ForeignKey(
        Contact,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Contact"),
    )
    debit = models.DecimalField(
        max_digits=19, decimal_places=2, null=True, blank=True, verbose_name=_("Debit")
    )
    credit = models.DecimalField(
        max_digits=19, decimal_places=2, null=True, blank=True, verbose_name=_("Credit")
    )

    row_order = models.PositiveSmallIntegerField(
        null=True, blank=True, verbose_name=_("row order")
    )

    def __str__(self):
        return f"{self.description} in {self.document}"

    class Meta:
        verbose_name = _("General journal document line")
        verbose_name_plural = _("General journal document lines")
        ordering = ("-document__date", "row_order")


class GeneralJournalDocumentResourceType(
    resources.GeneralJournalDocumentResourceType, JournalDocumentResourceType
):
    model = GeneralJournalDocument
    document_lines_model = GeneralJournalDocumentLine

    @classmethod
    def get_document_line_resource_data(cls, data: MoneybirdResource):
        return data["general_journal_document_entries"]

    @classmethod
    def get_model_kwargs(cls, data):
        kwargs = super().get_model_kwargs(data)
        kwargs["reference"] = data["reference"]
        kwargs["date"] = datetime.datetime.fromisoformat(data["date"]).date()
        return kwargs

    @classmethod
    def get_document_line_model_kwargs(cls, line_data: MoneybirdResource, document):
        kwargs = super().get_document_line_model_kwargs(line_data, document)
        kwargs["document"] = document
        kwargs["debit"] = Decimal(line_data["debit"])
        kwargs["credit"] = Decimal(line_data["credit"])

        kwargs["total_amount"] = Decimal(line_data["debit"]) - Decimal(
            line_data["credit"]
        )
        kwargs["contact"] = ContactResourceType.get_or_create_from_moneybird_data(
            line_data["contact_id"]
        )
        return kwargs

    @classmethod
    def serialize_for_moneybird(cls, instance):
        data = super().serialize_for_moneybird(instance)
        data["reference"] = instance.reference
        data["date"] = instance.date.isoformat()
        return data

    @classmethod
    def serialize_document_line_for_moneybird(cls, document_line, document):
        data = super().serialize_document_line_for_moneybird(document_line, document)
        if document_line.debit:
            data["debit"] = float(document_line.debit)
        if document_line.credit:
            data["credit"] = float(document_line.credit)
        if document_line.contact:
            data["contact_id"] = document_line.contact.moneybird_id
        data["row_order"] = document_line.row_order
        return data

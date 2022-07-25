from django.db import models
from django.utils.translation import gettext as _

from accounting.models.ledger_account import (
    LedgerAccount,
    LedgerAccountResourceType,
)
from accounting.models.project import Project, ProjectResourceType
from moneybird.models import (
    MoneybirdDocumentLineModel,
)
from moneybird.resource_types import (
    MoneybirdResourceTypeWithDocumentLines,
    MoneybirdResource,
)


class JournalDocumentLine(MoneybirdDocumentLineModel):
    description = models.TextField(verbose_name=_("Description"), null=True, blank=True)
    total_amount = models.DecimalField(
        max_digits=19,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Total amount"),
    )
    ledger_account = models.ForeignKey(
        LedgerAccount,
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
        verbose_name=_("Ledger account"),
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Project"),
    )

    @property
    def document(self):
        if self.purchasedocumentline:
            return self.purchasedocumentline.document
        if self.salesinvoicedocumentline:
            return self.salesinvoicedocumentline.document
        if self.generaljournaldocumentline:
            return self.generaljournaldocumentline.document


    def __str__(self):
        return f"Document line {self.moneybird_id}"

    class Meta:
        verbose_name = _("Journal document line")
        verbose_name_plural = _("Journal document lines")


class JournalDocumentResourceType(MoneybirdResourceTypeWithDocumentLines):
    document_lines_model = JournalDocumentLine
    document_lines_foreign_key = "document_lines"
    document_foreign_key = "document"

    @classmethod
    def get_document_line_model_kwargs(cls, line_data: MoneybirdResource, document):
        kwargs = super().get_document_line_model_kwargs(line_data, document)
        kwargs["description"] = line_data["description"]
        kwargs[
            "ledger_account"
        ] = LedgerAccountResourceType.get_or_create_from_moneybird_data(
            line_data["ledger_account_id"]
        )
        kwargs["project"] = ProjectResourceType.get_or_create_from_moneybird_data(
            line_data["project_id"]
        )
        return kwargs

    @classmethod
    def serialize_document_line_for_moneybird(cls, document_line, document):
        data = super().serialize_document_line_for_moneybird(document_line, document)
        data["description"] = document_line.description
        data["ledger_account_id"] = document_line.ledger_account.moneybird_id
        if document_line.project:
            data["project_id"] = document_line.project.moneybird_id
        return data

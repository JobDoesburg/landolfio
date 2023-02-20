from django.db import models
from django.db.models import Case, When, Q, F
from django.utils.translation import gettext_lazy as _
from model_utils.managers import (
    InheritanceManagerMixin,
    InheritanceQuerySetMixin,
)

from queryable_properties.managers import (
    QueryablePropertiesManager,
    QueryablePropertiesQuerySet,
)

from queryable_properties.properties import AnnotationProperty

from accounting.models import Contact
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


class JournalDocumentLineQueryset(
    InheritanceQuerySetMixin, QueryablePropertiesQuerySet
):
    pass


class JournalDocumentLineManager(InheritanceManagerMixin, QueryablePropertiesManager):
    _queryset_class = JournalDocumentLineQueryset
    use_for_related_fields = True

    def get_queryset(self):
        return super().get_queryset().select_subclasses()


class JournalDocumentLine(MoneybirdDocumentLineModel):
    objects = JournalDocumentLineManager()

    description = models.TextField(verbose_name=_("description"), null=True, blank=True)
    total_amount = models.DecimalField(
        max_digits=19,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("total amount"),
    )
    ledger_account = models.ForeignKey(
        LedgerAccount,
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
        verbose_name=_("ledger account"),
    )
    contact = models.ForeignKey(
        Contact,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("contact"),
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("project"),
    )

    document = AnnotationProperty(
        Case(
            When(
                Q(purchasedocumentline__isnull=False),
                then=F("purchasedocumentline__document"),
            ),
            When(
                Q(salesinvoicedocumentline__isnull=False),
                then=F("salesinvoicedocumentline__document"),
            ),
            When(
                Q(generaljournaldocumentline__isnull=False),
                then=F("generaljournaldocumentline__document"),
            ),
            default=None,
        )
    )

    date = AnnotationProperty(F("document__date"))

    def __str__(self):
        return f"{self.description} in {self.document}"

    class Meta:
        verbose_name = _("journal document line")
        verbose_name_plural = _("journal document lines")
        base_manager_name = "objects"


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

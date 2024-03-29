import datetime
from decimal import Decimal

from django.db import models
from django.db.models import F
from django.utils.translation import gettext_lazy as _
from queryable_properties.properties import AnnotationProperty
from queryable_properties.managers import QueryablePropertiesManager

from accounting.models import (
    DocumentStyle,
    TaxRate,
    TaxRateTypes,
    Product,
    Project,
    LedgerAccount,
    TaxRateResourceType,
    ProjectResourceType,
    LedgerAccountResourceType,
    ProductResourceType,
    LedgerAccountType,
    DocumentStyleResourceType,
)
from accounting.models.contact import Contact, ContactResourceType
from accounting.models.workflow import Workflow, WorkflowResourceType, WorkflowTypes
from moneybird import resources
from moneybird.models import (
    SynchronizableMoneybirdResourceModel,
    MoneybirdDocumentLineModel,
)
from moneybird.resource_types import MoneybirdResourceId, MoneybirdResource


class EstimateStates(models.TextChoices):
    DRAFT = "draft", _("draft")
    OPEN = "open", _("open")
    LATE = "late", _("late")
    ACCEPTED = "accepted", _("accepted")
    REJECTED = "rejected", _("rejected")
    BILLED = "billed", _("billed")
    ARCHIVED = "archived", _("archived")
    SCHEDULED = "scheduled", _("scheduled")


class Estimate(SynchronizableMoneybirdResourceModel):
    contact = models.ForeignKey(
        Contact,
        null=True,
        blank=False,
        on_delete=models.SET_NULL,
        verbose_name=_("contact"),
        related_name="estimates",
    )
    estimate_id = models.CharField(
        max_length=255, null=True, blank=True, verbose_name=_("estimate id")
    )
    draft_id = models.CharField(
        max_length=255, null=True, blank=True, verbose_name=_("draft id")
    )
    workflow = models.ForeignKey(
        Workflow,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={"active": True, "type": WorkflowTypes.ESTIMATE_WORKFLOW},
        verbose_name=_("workflow"),
    )
    document_style = models.ForeignKey(
        DocumentStyle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("document style"),
    )
    state = models.CharField(
        max_length=10,
        choices=EstimateStates.choices,
        verbose_name=_("state"),
        default=EstimateStates.DRAFT,
    )

    total_price = models.DecimalField(
        max_digits=19, decimal_places=2, verbose_name=_("total price"), null=True
    )

    estimate_date = models.DateField(
        null=True, blank=True, verbose_name=_("estimate date")
    )
    due_date = models.DateField(null=True, blank=True, verbose_name=_("due date"))
    reference = models.CharField(
        max_length=255, null=True, blank=True, verbose_name=_("reference")
    )
    discount = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("discount"),
    )
    original_estimate = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("original estimate"),
    )
    sent_at = models.DateField(null=True, blank=True, verbose_name=_("sent at"))
    accepted_at = models.DateField(null=True, blank=True, verbose_name=_("accepted at"))
    rejected_at = models.DateField(null=True, blank=True, verbose_name=_("rejected at"))
    archived_at = models.DateField(null=True, blank=True, verbose_name=_("archived at"))
    public_view_code = models.CharField(
        max_length=10, null=True, verbose_name=_("public view code")
    )
    url = models.URLField(null=True, max_length=2048, verbose_name=_("url"))
    pre_text = models.TextField(null=True, blank=True, verbose_name=_("pre text"))
    post_text = models.TextField(null=True, blank=True, verbose_name=_("post text"))
    prices_are_incl_tax = models.BooleanField(
        default=True, verbose_name=_("prices are incl. tax")
    )

    def __str__(self):
        if self.draft_id:
            return f"{_('draft')} {self.draft_id}"
        return f"{self.estimate_id}"

    class Meta:
        verbose_name = _("estimate")
        verbose_name_plural = _("estimates")
        ordering = ("-draft_id", "-estimate_date", "-estimate_id")


class EstimateDocumentLine(MoneybirdDocumentLineModel):
    objects = QueryablePropertiesManager()
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
    project = models.ForeignKey(
        Project,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("project"),
    )
    amount = models.CharField(
        verbose_name=_("amount"), null=True, blank=True, default="1 x", max_length=255
    )
    amount_decimal = models.DecimalField(
        null=True,
        max_digits=19,
        decimal_places=2,
        blank=True,
        verbose_name=_("amount (decimal)"),
    )
    price = models.DecimalField(
        max_digits=19, decimal_places=2, verbose_name=_("price")
    )
    document = models.ForeignKey(
        Estimate,
        on_delete=models.CASCADE,
        verbose_name=_("document"),
        related_name="document_lines",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("product"),
    )
    tax_rate = models.ForeignKey(
        TaxRate,
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
        verbose_name=_("tax rate"),
        limit_choices_to={"active": True, "type": TaxRateTypes.SALES_INVOICE},
    )
    row_order = models.PositiveSmallIntegerField(
        null=True, blank=True, verbose_name=_("row order")
    )

    date = AnnotationProperty(F("document__estimate_date"))

    @property
    def contact(self):
        return self.document.contact

    def __str__(self):
        return f"{self.amount} {self.description} in {self.document}"

    class Meta:
        verbose_name = _("estimate document line")
        verbose_name_plural = _("estimate document lines")
        ordering = ("-document__estimate_date", "row_order")


class EstimateResourceType(resources.EstimateResourceType):
    model = Estimate
    document_lines_model = EstimateDocumentLine
    document_lines_foreign_key = "document_lines"
    document_foreign_key = "document"

    @classmethod
    def get_model_kwargs(cls, data):
        kwargs = super().get_model_kwargs(data)
        kwargs["contact"] = ContactResourceType.get_or_create_from_moneybird_data(
            data["contact_id"]
        )
        if data["draft_id"]:
            kwargs["draft_id"] = data["draft_id"]
        if data.get("estimate_id"):
            kwargs["estimate_id"] = data["estimate_id"]
        kwargs["workflow"] = WorkflowResourceType.get_or_create_from_moneybird_data(
            data["workflow_id"]
        )
        kwargs[
            "document_style"
        ] = DocumentStyleResourceType.get_or_create_from_moneybird_data(
            data["document_style_id"]
        )
        if data.get("original_estimate_id"):
            kwargs[
                "original_estimate"
            ] = EstimateResourceType.get_or_create_from_moneybird_data(
                data["original_estimate_id"]
            )
        kwargs["state"] = EstimateStates(data["state"])
        kwargs["total_price"] = data["total_price_incl_tax_base"]
        if data.get("estimate_date"):
            kwargs["estimate_date"] = datetime.datetime.fromisoformat(
                data["estimate_date"]
            ).date()
        if data.get("due_date"):
            kwargs["due_date"] = datetime.datetime.fromisoformat(
                data["due_date"]
            ).date()
        kwargs["reference"] = data["reference"]
        kwargs["discount"] = data["discount"]
        if data.get("sent_at"):
            kwargs["sent_at"] = datetime.datetime.fromisoformat(data["sent_at"]).date()
        if data.get("accepted_at"):
            kwargs["accepted_at"] = datetime.datetime.fromisoformat(
                data["accepted_at"]
            ).date()
        if data.get("rejected_at"):
            kwargs["rejected_at"] = datetime.datetime.fromisoformat(
                data["rejected_at"]
            ).date()
        if data.get("archived_at"):
            kwargs["archived_at"] = datetime.datetime.fromisoformat(
                data["archived_at"]
            ).date()
        kwargs["public_view_code"] = data["public_view_code"]
        kwargs["url"] = data["url"]
        if data.get("pre_text"):
            kwargs["pre_text"] = data["pre_text"]
        if data.get("post_text"):
            kwargs["post_text"] = data["post_text"]
        kwargs["prices_are_incl_tax"] = data["prices_are_incl_tax"]
        return kwargs

    @classmethod
    def get_document_line_model_kwargs(cls, line_data: MoneybirdResource, document):
        kwargs = super().get_document_line_model_kwargs(line_data, document)
        kwargs["document"] = document
        kwargs["description"] = line_data["description"]
        kwargs[
            "ledger_account"
        ] = LedgerAccountResourceType.get_or_create_from_moneybird_data(
            line_data["ledger_account_id"]
        )
        kwargs["project"] = ProjectResourceType.get_or_create_from_moneybird_data(
            line_data["project_id"]
        )
        kwargs["amount"] = line_data["amount"]
        kwargs["amount_decimal"] = line_data["amount_decimal"]
        kwargs["row_order"] = line_data["row_order"]
        kwargs["price"] = line_data["price"]
        kwargs["tax_rate"] = TaxRateResourceType.get_or_create_from_moneybird_data(
            line_data["tax_rate_id"]
        )
        kwargs["product"] = ProductResourceType.get_or_create_from_moneybird_data(
            line_data["product_id"]
        )
        kwargs["total_amount"] = line_data["total_price_excl_tax_with_discount_base"]
        ledger_account = kwargs["ledger_account"]
        if (
            ledger_account
            and ledger_account.account_type
            and ledger_account.account_type == LedgerAccountType.NON_CURRENT_ASSETS
        ):
            kwargs["total_amount"] = -1 * Decimal(
                kwargs["total_amount"]
            )  # TODO is dit handig?
        return kwargs

    @classmethod
    def serialize_for_moneybird(cls, instance):
        data = super().serialize_for_moneybird(instance)
        if instance.contact:
            data["contact_id"] = MoneybirdResourceId(instance.contact.moneybird_id)
        if instance.workflow:
            data["workflow_id"] = MoneybirdResourceId(instance.workflow.moneybird_id)
        if instance.document_style:
            data["document_style_id"] = MoneybirdResourceId(
                instance.document_style.moneybird_id
            )
        data["reference"] = instance.reference or ""
        if instance.estimate_date:
            data["estimate_date"] = instance.estimate_date.isoformat()
        if instance.due_date:
            data["due_date"] = instance.due_date.isoformat()
        data["prices_are_incl_tax"] = instance.prices_are_incl_tax
        data["discount"] = instance.discount
        data["pre_text"] = instance.pre_text
        data["post_text"] = instance.post_text
        return data

    @classmethod
    def serialize_document_line_for_moneybird(cls, document_line, document):
        data = super().serialize_document_line_for_moneybird(document_line, document)
        data["description"] = document_line.description
        if document_line.ledger_account and document_line.ledger_account.moneybird_id:
            data["ledger_account_id"] = document_line.ledger_account.moneybird_id

        if document_line.project and document_line.project.moneybird_id:
            data["project_id"] = document_line.project.moneybird_id

        data["amount"] = document_line.amount
        data["row_order"] = document_line.row_order
        data["price"] = float(document_line.price)
        if document_line.ledger_account:
            data["ledger_account_id"] = MoneybirdResourceId(
                document_line.ledger_account.moneybird_id
            )
            if (
                document_line.ledger_account.account_type
                and document_line.ledger_account.account_type
                == LedgerAccountType.NON_CURRENT_ASSETS
            ):
                data["price"] = float(-1 * document_line.price)  # TODO is dit handig?
        return data

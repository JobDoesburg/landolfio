from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.functions import datetime
from django.utils.translation import gettext as _
from django_countries.fields import CountryField
from localflavor.generic.countries.sepa import IBAN_SEPA_COUNTRIES
from localflavor.generic.models import IBANField, BICField

from accounting.models.workflow import Workflow, WorkflowTypes, WorkflowResourceType
from moneybird import resources
from moneybird.models import (
    SynchronizableMoneybirdResourceModel,
)


class SepaSequenceTypes(models.TextChoices):
    RECURRING = "RCUR", _("Recurring")
    FIRST = "FRST", _("First")
    FINAL = "FNAL", _("Final")
    ONE_OFF = "OOFF", _("One-off")


class Contact(SynchronizableMoneybirdResourceModel):
    company_name = models.CharField(
        verbose_name=_("company name"),
        max_length=255,
        null=True,
        blank=True,
    )
    first_name = models.CharField(
        verbose_name=_("first name"),
        max_length=255,
        null=True,
        blank=True,
    )
    last_name = models.CharField(
        verbose_name=_("last name"),
        max_length=255,
        null=True,
        blank=True,
    )
    address_1 = models.CharField(
        verbose_name=_("address 1"),
        max_length=255,
        null=True,
        blank=True,
    )
    address_2 = models.CharField(
        verbose_name=_("address 2"),
        max_length=255,
        null=True,
        blank=True,
    )
    zip_code = models.CharField(
        verbose_name=_("zip code"),
        max_length=50,
        null=True,
        blank=True,
    )
    city = models.CharField(
        verbose_name=_("city"),
        max_length=255,
        null=True,
        blank=True,
    )
    country = CountryField(verbose_name=_("country"), default="NL")
    phone = models.CharField(
        verbose_name=_("phone"),
        max_length=255,
        null=True,
        blank=True,
    )
    customer_id = models.CharField(
        verbose_name=_("customer id"),
        max_length=255,
        null=True,
        blank=True,
    )
    tax_number = models.CharField(
        verbose_name=_("tax number"),
        max_length=50,
        null=True,
        blank=True,
    )
    chamber_of_commerce = models.CharField(
        verbose_name=_("chamber of commerce"),
        max_length=50,
        null=True,
        blank=True,
    )
    bank_account = IBANField(
        verbose_name=_("bank account"),
        include_countries=IBAN_SEPA_COUNTRIES,
        blank=True,
        null=True,
    )
    attention = models.CharField(
        verbose_name=_("attention"),
        max_length=255,
        null=True,
        blank=True,
    )
    email = models.EmailField(
        verbose_name=_("email"),
        null=True,
        blank=True,
    )
    email_ubl = models.BooleanField(verbose_name=_("email ubl"), default=False)
    send_invoices_to_attention = models.CharField(
        verbose_name=_("send invoices to (attention)"),
        max_length=255,
        null=True,
        blank=True,
    )
    send_invoices_to_email = models.EmailField(
        verbose_name=_("send invoices to (email)"),
        null=True,
        blank=True,
    )
    send_estimates_to_attention = models.CharField(
        verbose_name=_("send estimates to (attention)"),
        max_length=255,
        null=True,
        blank=True,
    )
    send_estimates_to_email = models.EmailField(
        verbose_name=_("send estimates to (email)"),
        null=True,
        blank=True,
    )
    sepa_active = models.BooleanField(verbose_name=_("SEPA active"), default=False)
    sepa_iban = IBANField(
        verbose_name=_("SEPA IBAN"),
        include_countries=IBAN_SEPA_COUNTRIES,
        blank=True,
        null=True,
    )
    sepa_iban_account_name = models.CharField(
        verbose_name=_("SEPA IBAN account name"),
        max_length=255,
        null=True,
        blank=True,
    )
    sepa_bic = BICField(verbose_name=_("SEPA BIC"), blank=True, null=True)
    sepa_mandate_id = models.CharField(
        verbose_name=_("SEPA mandate id"),
        max_length=50,
        null=True,
        blank=True,
    )
    sepa_mandate_date = models.DateField(
        verbose_name=_("SEPA mandate date"), null=True, blank=True
    )
    sepa_sequence_type = models.CharField(
        verbose_name=_("SEPA sequence type"),
        max_length=4,
        null=True,
        blank=True,
        choices=SepaSequenceTypes.choices,
    )
    tax_number_valid = models.BooleanField(
        verbose_name=_("tax number valid"), default=False
    )
    invoice_workflow = models.ForeignKey(
        Workflow,
        verbose_name=_("default invoice workflow"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={"active": True, "type": WorkflowTypes.INVOICE_WORKFLOW},
        related_name="invoice_workflow_contacts",
    )
    estimate_workflow = models.ForeignKey(
        Workflow,
        verbose_name=_("default estimate workflow"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={"active": True, "type": WorkflowTypes.ESTIMATE_WORKFLOW},
        related_name="estimate_workflow_contacts",
    )
    sales_invoices_url = models.URLField(
        verbose_name=_("sales invoices url"), blank=True, max_length=2048, null=True
    )

    def clean(self):
        super().clean()
        errors = {}

        if not any([self.company_name, self.first_name, self.last_name]):
            errors.update(
                {
                    "company_name": _(
                        "Contact must either have a company name, or first and last name."
                    )
                }
            )
            errors.update(
                {
                    "first_name": _(
                        "Contact must either have a company name, or first and last name."
                    )
                }
            )
            errors.update(
                {
                    "last_name": _(
                        "Contact must either have a company name, or first and last name."
                    )
                }
            )

        sepa_fields = [
            "sepa_iban",
            "sepa_iban_account_name",
            "sepa_bic",
            "sepa_mandate_id",
            "sepa_mandate_date",
            "sepa_sequence_type",
        ]
        if self.sepa_active and not all(
            [getattr(self, field, None) for field in sepa_fields]
        ):
            for field in sepa_fields:
                if getattr(self, field, None) is None:
                    errors.update(
                        {field: _("Fill in all SEPA fields if SEPA mandate is active.")}
                    )

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        if self.company_name:
            return self.company_name
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = _("contact")
        verbose_name_plural = _("contacts")
        ordering = ["company_name", "last_name", "first_name"]


class ContactResourceType(resources.ContactResourceType):
    model = Contact

    @classmethod
    def get_model_kwargs(cls, resource_data):
        kwargs = super().get_model_kwargs(resource_data)
        kwargs["company_name"] = resource_data["company_name"]
        kwargs["first_name"] = resource_data["firstname"]
        kwargs["last_name"] = resource_data["lastname"]
        kwargs["address_1"] = resource_data["address1"]
        kwargs["address_2"] = resource_data["address2"]
        kwargs["zip_code"] = resource_data["zipcode"]
        kwargs["city"] = resource_data["city"]
        kwargs["country"] = resource_data["country"]
        kwargs["phone"] = resource_data["phone"]
        kwargs["customer_id"] = resource_data["customer_id"]
        kwargs["tax_number"] = resource_data["tax_number"]
        kwargs["chamber_of_commerce"] = resource_data["chamber_of_commerce"]
        kwargs["bank_account"] = resource_data["bank_account"]
        kwargs["attention"] = resource_data["attention"]
        kwargs["email"] = resource_data["email"]
        kwargs["email_ubl"] = resource_data["email_ubl"]
        kwargs["send_invoices_to_attention"] = resource_data[
            "send_invoices_to_attention"
        ]
        kwargs["send_invoices_to_email"] = resource_data["send_invoices_to_email"]
        kwargs["send_estimates_to_attention"] = resource_data[
            "send_estimates_to_attention"
        ]
        kwargs["send_estimates_to_email"] = resource_data["send_estimates_to_email"]
        kwargs["sepa_active"] = resource_data["sepa_active"]
        kwargs["sepa_iban"] = resource_data["sepa_iban"]
        kwargs["sepa_iban_account_name"] = resource_data["sepa_iban_account_name"]
        kwargs["sepa_bic"] = resource_data["sepa_bic"]
        kwargs["sepa_mandate_id"] = resource_data["sepa_mandate_id"]
        kwargs["sepa_mandate_date"] = (
            datetime.datetime.fromisoformat(resource_data["sepa_mandate_date"]).date()
            if resource_data["sepa_mandate_date"]
            else None
        )
        kwargs["sepa_sequence_type"] = resource_data["sepa_sequence_type"]
        kwargs["tax_number_valid"] = resource_data["tax_number_valid"] or False
        kwargs[
            "invoice_workflow"
        ] = WorkflowResourceType.get_or_create_from_moneybird_data(
            resource_data["invoice_workflow_id"]
        )
        kwargs[
            "estimate_workflow"
        ] = WorkflowResourceType.get_or_create_from_moneybird_data(
            resource_data["estimate_workflow_id"]
        )
        kwargs["sales_invoices_url"] = resource_data["sales_invoices_url"]
        return kwargs

    @classmethod
    def serialize_for_moneybird(cls, instance):
        data = super().serialize_for_moneybird(instance)
        data["company_name"] = instance.company_name or ""
        data["firstname"] = instance.first_name or ""
        data["lastname"] = instance.last_name or ""
        data["address1"] = instance.address_1 or ""
        data["address2"] = instance.address_2 or ""
        data["zipcode"] = instance.zip_code or ""
        data["city"] = instance.city or ""
        data["country"] = instance.country.code
        data["phone"] = instance.phone or ""
        data["customer_id"] = instance.customer_id or ""
        data["tax_number"] = instance.tax_number or ""
        data["chamber_of_commerce"] = instance.chamber_of_commerce or ""
        data["bank_account"] = instance.bank_account or ""
        data["attention"] = instance.attention or ""  # ???

        data["email_ubl"] = instance.email_ubl
        data["send_invoices_to_attention"] = instance.send_invoices_to_attention or ""
        data["send_invoices_to_email"] = instance.send_invoices_to_email
        data["send_estimates_to_attention"] = instance.send_estimates_to_attention or ""
        data["send_estimates_to_email"] = instance.send_estimates_to_email
        data["sepa_active"] = instance.sepa_active
        data["sepa_iban"] = instance.sepa_iban or ""
        data["sepa_iban_account_name"] = instance.sepa_iban_account_name or ""
        data["sepa_bic"] = instance.sepa_bic or ""
        data["sepa_mandate_id"] = instance.sepa_mandate_id or ""
        data["sepa_mandate_date"] = (
            instance.sepa_mandate_date.isoformat()
            if instance.sepa_mandate_date
            else None
        )
        data["sepa_sequence_type"] = instance.sepa_sequence_type

        data["invoice_workflow_id"] = (
            instance.invoice_workflow.moneybird_id
            if instance.invoice_workflow
            else None
        )
        data["estimate_workflow_id"] = (
            instance.estimate_workflow.moneybird_id
            if instance.estimate_workflow
            else None
        )

        data["send_invoices_to_email"] = instance.email
        data["send_estimates_to_email"] = instance.email
        return data


# class PaymentsMandateResourceType(resources.PaymentsMandateResourceType):
#     model = Contact
#
#     @classmethod
#     def process_webhook_event(
#         cls,
#         resource_id: MoneybirdResourceId,
#         data: MoneybirdResource,
#         event: WebhookEvent,
#     ):
#         return
#
#
#     @classmethod
#     def create_instance_from_moneybird(cls, resource_data: MoneybirdResource):
#         # 1. Get contact from resource data
#         # 2. Change the field
#         return
#
#     @classmethod
#     def update_from_moneybird(cls, resource_data: MoneybirdResource, obj=None):
#         return
#
#     def cr

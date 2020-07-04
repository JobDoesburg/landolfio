from typing import Dict, Any

from django.db import models
from django.conf import settings
from django.db.models import PROTECT

from django_countries.fields import CountryField
from django_iban.fields import IBANField


# TODO create MoneybirdSimpleResourceModel for models without Synchronization endpoint:
# Entities you can only get:
# workflow, tax rate, document_style, custom_field
# Entities you can get and post/patch but not sync
# project, product, ledger_accounts, identity (+/default),
# Entities that are MoneybirdSynchronizableResourceModel
# general document, general journal document, purchase invoice, receipt, typeless document


class MoneybirdSynchronizableResourceModel(models.Model):
    """
    Objects that can be synced with Moneybird resources.

    Those objects are expected to be reachable from the Moneybird API on their
    `moneybird_resource_path_name` with a "/synchronization" postfix. The object's
    `id` and `version` are used to synchronize data with Moneybird.
    Attributes are expected to have names equal to those used in the Moneybird API,
    all other attributes are ignored on synchronization.

    For more details, check out https://developer.moneybird.com
    """

    class Meta:
        abstract = True

    moneybird_resource_path_name = None
    moneybird_resource_name = None

    moneybird_base_fields = ["id", "version"]  # Base fields of every MoneybirdSynchronizableResourceModel
    moneybird_data_fields = (
        []
    )  # Fields of a MoneybirdSynchronizableResourceModel that are communicated with the Moneybird API. ForeignKey fields to other MoneybirdSynchronizableResourceModel are expected to be entered with _id postfix even though this is not the field name, as Django automatically creates the _id attribute and this is used in the backend by both Django and Moneybird. Must all be attributes in the model
    moneybird_readonly_base_fields = [
        "id",
        "version",
    ]  # Base fields that should only be set by Moneybird and thus never written to Moneybird. Must be subset of the moneybird_base_fields
    moneybird_readonly_data_fields = (
        []
    )  # Fields of a MoneybirdSynchronizableResourceModel that should only be set by Moneybird and thus never written to Moneybird. This does NOT make them readonly in an Admin, nor prevents setting them. It only prevents writing them to Moneybird. Must be subset of the moneybird_data_fields

    processed = False  # If True, saving this object will not trigger a create or patch call to Moneybird. Used when synchronizing Moneybird objects.

    id = models.CharField(
        primary_key=True,
        max_length=20,
        help_text="This is the primary key of this object, both for this application and in Moneybird.",
    )
    version = models.IntegerField(
        null=True,
        blank=True,
        unique=True,
        help_text="This is the Moneybird version of the currently stored data and is used when looking for changes efficiently.",
    )

    @classmethod
    def get_moneybird_resource_path_name(cls):
        if cls.moneybird_resource_path_name:
            return cls.moneybird_resource_path_name
        else:
            raise NotImplementedError

    @classmethod
    def get_moneybird_resource_name(cls):
        if cls.moneybird_resource_name:
            return cls.moneybird_resource_name
        else:
            raise NotImplementedError

    @classmethod
    def get_moneybird_fields(cls):
        return cls.moneybird_base_fields + cls.moneybird_data_fields

    @classmethod
    def get_moneybird_readonly_fields(cls):
        return cls.moneybird_readonly_base_fields + cls.moneybird_readonly_data_fields

    def get_moneybird_attr(self, field):
        if field in self.get_moneybird_fields():
            return getattr(self, field, None)

    def set_moneybird_attr(self, field, value):
        if field in self.get_moneybird_fields():
            return setattr(self, field, value)

    def get_moneybird_resource_data(self):
        result = {}
        for field in self.get_moneybird_fields():
            attr = self.get_moneybird_attr(field)
            result[field] = attr
        return result

    def set_moneybird_resource_data(self, data: Dict[str, Any]):
        for field in data:  # TODO parse extra resources
            if field in self.get_moneybird_fields():
                self.set_moneybird_attr(field, data[field])
        return self

    @property
    def moneybird_resource_url(self):
        return (
            f"https://moneybird.com/{settings.MONEYBIRD_ADMINISTRATION_ID}/{self.get_moneybird_resource_path_name()}/{self.id}"
            if self.id
            else None
        )

    def get_absolute_url(self):
        return self.moneybird_resource_url


class Contact(MoneybirdSynchronizableResourceModel):
    class Meta:
        verbose_name = "contact"
        verbose_name_plural = "contacts"

    moneybird_resource_path_name = "contacts"
    moneybird_resource_name = "contact"

    moneybird_data_fields = [
        "company_name",
        "firstname",
        "lastname",
        "attention",
        "address1",
        "address2",
        "zipcode",
        "city",
        "country",
        "phone",
        "delivery_method",
        "send_invoices_to_attention",
        "send_invoices_to_email",
        "send_estimates_to_attention",
        "send_estimates_to_email",
        "email",
        "email_ubl",
        "customer_id",
        "chamber_of_commerce",
        "tax_number",
        "bank_account",
        "sepa_active",
        "sepa_iban",
        "sepa_iban_account_name",
        "sepa_bic",
        "sepa_mandate_id",
        "sepa_sequence_type",
    ]
    moneybird_readonly_data_fields = ["attention", "email"]

    DELIVERY_METHOD_EMAIL = "Email"
    DELIVERY_METHOD_SIMPLERINVOICING = "Simplerinvoicing"
    DELIVERY_METHOD_POST = "Post"
    DELIVERY_METHOD_MANUAL = "Manual"
    DELIVERY_METHOD_CHOICES = (
        (DELIVERY_METHOD_EMAIL, "Email"),
        (DELIVERY_METHOD_SIMPLERINVOICING, "Simplerinvoicing"),
        (DELIVERY_METHOD_POST, "Post"),
        (DELIVERY_METHOD_MANUAL, "Manual"),
    )

    SEPA_RCUR = "RCUR"
    SEPA_FRST = "FRST"
    SEPA_OOFF = "OOFF"
    SEPA_FNAL = "FNAL"
    SEPA_SEQUENCE_TYPE_CHOICES = (
        (SEPA_RCUR, "RCUR"),
        (SEPA_FRST, "FRST"),
        (SEPA_OOFF, "OOFF"),
        (SEPA_FNAL, "FNAL"),
    )

    company_name = models.CharField(blank=True, null=True, max_length=100)
    firstname = models.CharField(blank=True, null=True, max_length=100)
    lastname = models.CharField(blank=True, null=True, max_length=100)
    address1 = models.CharField(blank=True, null=True, max_length=100)
    address2 = models.CharField(blank=True, null=True, max_length=100)
    zipcode = models.CharField(blank=True, null=True, max_length=10)
    city = models.CharField(blank=True, null=True, max_length=100)
    country = CountryField(
        blank=True,
        null=True,
        help_text="Will be automatically set to the standard Moneybird administration country if empty.",
    )
    phone = models.CharField(blank=True, null=True, max_length=100)
    delivery_method = models.CharField(
        blank=True, null=True, choices=DELIVERY_METHOD_CHOICES, default=DELIVERY_METHOD_EMAIL, max_length=16
    )
    customer_id = models.IntegerField(
        blank=True,
        null=True,
        help_text="Will be assigned automatically if empty. Should be unique for the administration.",
    )
    tax_number = models.CharField(blank=True, null=True, max_length=100)
    chamber_of_commerce = models.CharField(blank=True, null=True, max_length=100)
    bank_account = models.CharField(blank=True, null=True, max_length=100)
    attention = models.CharField(blank=True, null=True, max_length=100)

    email = models.CharField(blank=True, null=True, max_length=200,)
    email_ubl = models.BooleanField(blank=True, null=True)
    send_invoices_to_attention = models.CharField(blank=True, null=True, max_length=100)
    send_invoices_to_email = models.CharField(
        blank=True, null=True, max_length=200, help_text="Can be a single email or a comma-separated list of emails"
    )
    send_estimates_to_attention = models.CharField(blank=True, null=True, max_length=100)
    send_estimates_to_email = models.CharField(
        blank=True, null=True, max_length=200, help_text="Can be a single email or a comma-separated list of emails"
    )
    sepa_active = models.BooleanField(default=False, help_text="When true, all SEPA fields are required.")
    sepa_iban = IBANField(enforce_database_constraint=True, blank=True, null=True, max_length=100)
    sepa_iban_account_name = models.CharField(blank=True, null=True, max_length=100)
    sepa_bic = models.CharField(blank=True, null=True, max_length=100)
    sepa_mandate_id = models.CharField(blank=True, null=True, max_length=100)
    sepa_mandate_date = models.DateField(blank=True, null=True, help_text="Should be a date in the past.")
    sepa_sequence_type = models.CharField(blank=True, null=True, choices=SEPA_SEQUENCE_TYPE_CHOICES, max_length=4)
    # TODO add sales_invoices_url

    def get_moneybird_attr(self, field):
        if field == "country":
            return self.country.code
        return super(Contact, self).get_moneybird_attr(field)

    def set_moneybird_attr(self, field, value):
        if field == "country":
            self.country = value
        return super(Contact, self).set_moneybird_attr(field, value)

    def get_full_name(self):
        if self.firstname and self.lastname:
            return f"{self.firstname} {self.lastname}"
        elif self.firstname:
            return self.firstname
        return self.lastname

    def get_display_name(self):
        if self.company_name and self.get_full_name():
            return f"{self.company_name} ({self.get_full_name()})"
        elif self.company_name:
            return self.company_name
        return self.get_full_name()

    def __str__(self):
        if self.customer_id:
            return f"{self.get_display_name()} ({self.customer_id})"
        return self.get_display_name()

    # TODO refactor models in multiple files


class SalesInvoice(MoneybirdSynchronizableResourceModel):
    class Meta:
        verbose_name = "sales invoice"
        verbose_name_plural = "sales invoices"

    moneybird_resource_path_name = "sales_invoices"
    moneybird_resource_name = "sales_invoice"

    moneybird_data_fields = [
        "invoice_id",
        "draft_id",
        "contact_id",
        "workflow_id",
        "state",
        "reference",
        "invoice_date",
        "due_date",
        "discount",
        "paused",
        "paid_at",
        "sent_at",
        "payment_conditions",
        "payment_reference",
        "public_view_code",
        "total_paid",
        "total_unpaid",
        "total_unpaid_base",
        "total_price_excl_tax",
        "total_price_excl_tax_base",
        "total_price_incl_tax",
        "total_price_incl_tax_base",
        "total_discount",
        "prices_are_incl_tax",
    ]
    moneybird_readonly_data_fields = [
        "invoice_id",
        "draft_id",
        "state",
        "paid_at",
        "sent_at",
        "payment_reference",
        "public_view_code",
        "total_paid",
        "total_unpaid",
        "total_unpaid_base",
        "total_price_excl_tax",
        "total_price_excl_tax_base",
        "total_price_incl_tax",
        "total_price_incl_tax_base",
        "total_discount",
        "prices_are_incl_tax",
    ]

    # TODO include recurring_sales_invoice_id
    # TODO include original_sales_invoice_id

    # TODO include invoice detail lines etc

    invoice_id = models.CharField(unique=True, blank=True, null=True, max_length=20)
    draft_id = models.CharField(unique=True, blank=True, null=True, max_length=20)

    contact = models.ForeignKey(Contact, blank=False, null=False, on_delete=PROTECT)

    workflow_id = models.PositiveIntegerField(blank=True, null=True)

    STATE_DRAFT = "draft"
    STATE_OPEN = "open"
    STATE_SCHEDULED = "scheduled"
    STATE_PENDING_PAYMENT = "pending_payment"
    STATE_LATE = "late"
    STATE_REMINDED = "reminded"
    STATE_PAID = "paid"
    STATE_UNCOLLECTIBLE = "uncollectible"
    INVOICE_STATES = (
        (STATE_DRAFT, "draft"),
        (STATE_OPEN, "open"),
        (STATE_SCHEDULED, "scheduled"),
        (STATE_PENDING_PAYMENT, "pending_payment"),
        (STATE_LATE, "late"),
        (STATE_REMINDED, "reminded"),
        (STATE_PAID, "paid"),
        (STATE_UNCOLLECTIBLE, "uncollectible"),
    )

    # TODO add help texts

    state = models.CharField(blank=True, null=True, choices=INVOICE_STATES, max_length=100)

    reference = models.CharField(blank=True, null=True, max_length=1000)
    invoice_date = models.DateField(blank=True, null=True)  # TODO fix serialization
    due_date = models.DateField(blank=True, null=True)  # TODO fix serialization

    discount = models.DecimalField(blank=True, null=True, max_digits=3, decimal_places=2)  # TODO check serialization

    paused = models.BooleanField(blank=False, null=False, default=False)  # Make readonly, add action
    paid_at = models.DateField(blank=True, null=True)  # TODO fix serialization
    sent_at = models.DateField(blank=True, null=True)  # TODO fix serialization

    payment_conditions = models.CharField(blank=True, null=True, max_length=1000)
    payment_reference = models.CharField(blank=True, null=True, max_length=100)
    public_view_code = models.CharField(blank=True, null=True, max_length=100)

    total_paid = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2)
    total_unpaid = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2)
    total_unpaid_base = models.DecimalField(
        null=True, blank=True, max_digits=10, decimal_places=2
    )  # TODO check behaviour
    total_price_excl_tax = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2)
    total_price_excl_tax_base = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2)
    total_price_incl_tax = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2)
    total_price_incl_tax_base = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2)
    total_discount = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2)
    prices_are_incl_tax = models.BooleanField(default=True)

    def __str__(self):
        if self.state == SalesInvoice.STATE_DRAFT:
            return f"Draft {self.draft_id}"
        else:
            return f"{self.invoice_id} ({self.state})"

    def send(self):
        pass
        # post to "pause"

    def pause(self):
        pass
        # post to "resume"

    def send_reminder(self):
        pass
        # post to "resume"

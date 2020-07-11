from typing import Dict, Any, List

from django.db import models
from django.conf import settings
from django.db.models import PROTECT, CASCADE

from django_countries.fields import CountryField
from django_iban.fields import IBANField


# TODO create MoneybirdSimpleResourceModel for models without Synchronization endpoint:
# Entities you can only get:
# workflow, tax rate, document_style, custom_field
# Entities you can get and post/patch but not sync
# project, product, ledger_accounts, identity (+/default),
# Entities that are MoneybirdSynchronizableResourceModel
# general document, general journal document, purchase invoice, receipt, typeless document


class MoneybirdResourceModel(models.Model):
    """Objects that refer to models in Moneybird and can be accessed via the API."""

    class Meta:
        abstract = True

    moneybird_resource_name = None

    @classmethod
    def get_moneybird_resource_name(cls):
        if cls.moneybird_resource_name:
            return cls.moneybird_resource_name
        else:
            raise NotImplementedError

    id = models.CharField(
        primary_key=True,
        max_length=20,
        help_text="This is the primary key of this object, both for this application and in Moneybird.",
        editable=False,
    )

    moneybird_data_fields = []  # Fields that are managed by Moneybird
    moneybird_readonly_data_fields = (
        []
    )  # Fields that are only written by Moneybird and should not be written by Django
    moneybird_foreign_key_fields = (
        {}
    )  # Fields that refer to another MoneybirdResourceModel, like invoices have contacts. Use only for fields that should be passed to the Moneybird API
    moneybird_nested_data_fields = (
        {}
    )  # Fields that are the reversed relation of another MoneybirdResourceModel that have a foreign key to this object

    # TODO add sanity check whether the values above are in the correct subset of things etc

    @classmethod
    def get_moneybird_fields(cls):
        return cls.moneybird_data_fields + ["id"]

    @classmethod
    def get_moneybird_readonly_fields(cls):
        return cls.moneybird_readonly_data_fields + ["id"]

    @classmethod
    def get_moneybird_foreign_key_fields(cls):
        return cls.moneybird_foreign_key_fields

    @classmethod
    def get_moneybird_nested_data_fields(cls):
        return cls.moneybird_nested_data_fields

    processed = False  # If True, saving this object will not trigger a create or patch call to Moneybird. Used when synchronizing Moneybird objects.

    def get_moneybird_attr(self, field):
        if (
            field in self.get_moneybird_fields()
            or field in self.get_moneybird_foreign_key_fields()
            or field in self.get_moneybird_nested_data_fields()
        ):
            return getattr(self, field, None)

    def set_moneybird_attr(self, field, value):
        if field in self.get_moneybird_fields() or field in self.get_moneybird_foreign_key_fields():
            return setattr(self, field, value)

    def get_moneybird_resource_data(self):
        """Get a Moneybird-API supported data representation of this object."""
        result = {}
        for field in self.get_moneybird_fields():
            attr = self.get_moneybird_attr(field)
            result[field] = attr

        for field in self.get_moneybird_foreign_key_fields():  # Objects I have a foreign key to
            result[field] = self.get_moneybird_foreign_key_resource_data(field)

        for field in self.get_moneybird_nested_data_fields():  # Nested data objects that have a foreign key to me
            result[field + "_attributes"] = self.get_moneybird_nested_resource_data(field)

        return result

    def get_moneybird_nested_resource_data(self, field):
        """Get a Moneybird-API supported data representation of all nested objects."""
        if field in self.get_moneybird_nested_data_fields():
            nested_data = []
            for item in self.get_moneybird_attr(field).all():
                nested_data.append(item.get_moneybird_resource_data())
            return nested_data

    def get_moneybird_foreign_key_resource_data(self, field):
        """Get a Moneybird-API supported data representation of an object I have a foreign key to."""
        if field in self.get_moneybird_foreign_key_fields():
            return self.get_moneybird_attr(field).get_moneybird_resource_data()

    def set_moneybird_resource_data(self, data: Dict[str, Any]):
        """Update this object with data from the Moneybird API."""
        for field in data:

            if field in self.get_moneybird_foreign_key_fields():
                foreign_key_class = self._meta.get_field(field).remote_field.model
                if issubclass(foreign_key_class, MoneybirdSynchronizableResourceModel):
                    # If it is an independent object type, don't delete the current one
                    nested_data = data[field]
                    obj = foreign_key_class.update_or_create_object_from_moneybird(nested_data)
                    self.set_moneybird_attr(field, obj)
                elif issubclass(foreign_key_class, MoneybirdResourceModel):
                    nested_data = data[field]
                    current_obj = self.get_moneybird_attr(field)
                    if self.get_moneybird_attr(field).id != nested_data["id"]:
                        current_obj.processed = True
                        current_obj.delete()
                    obj = foreign_key_class.update_or_create_object_from_moneybird(nested_data)
                    self.set_moneybird_attr(field, obj)

            if field in self.get_moneybird_nested_data_fields():
                nested_data_class = self.get_moneybird_nested_data_fields()[field]
                if issubclass(nested_data_class, MoneybirdSynchronizableResourceModel):
                    pass  # Ignore independent object types, those will be synced independently
                elif issubclass(nested_data_class, MoneybirdNestedDataResourceModel):
                    nested_data = data[field]
                    if isinstance(
                        nested_data, list
                    ):  # Reversed foreign key are expected to be lists, as multiple can exist
                        current_objects = self.get_moneybird_attr(field).all()

                        to_delete = current_objects.exclude(id__in=[x["id"] for x in nested_data])
                        for delete_object in to_delete:
                            delete_object.processed = True
                            delete_object.delete()

                        new_objs = []
                        for obj_data in nested_data:
                            obj_data[nested_data_class.get_moneybird_nested_foreign_key() + "_id"] = self.id
                            obj = nested_data_class.update_or_create_object_from_moneybird(obj_data)
                            new_objs.append(obj)
                        # self.get_moneybird_attr(field).set(new_objs).save()  # technically this should not be required, as the reversed foreign key is already set

            if field in self.get_moneybird_fields():  # the default for simple fields
                self.set_moneybird_attr(field, data[field])

        return self

    @classmethod
    def update_or_create_object_from_moneybird(cls, data: Dict[str, Any]):
        obj = cls(id=data["id"]).set_moneybird_resource_data(data)
        obj.processed = True  # Prevent save() triggering a callback to Moneybird
        obj.save()
        return obj


class MoneybirdSynchronizableResourceModel(MoneybirdResourceModel):
    """
    Objects that can be synced with Moneybird resources.

    Those objects are expected to be reachable from the Moneybird API on their
    `moneybird_resource_path_name/synchronization` endpoint. The object's
    `id` and `version` are used to synchronize data with Moneybird.
    Attributes are expected to have names equal to those used in the Moneybird API,
    all other attributes are ignored on synchronization.

    For more details, check out https://developer.moneybird.com
    """

    class Meta:
        abstract = True

    moneybird_resource_path_name = None

    @classmethod
    def get_moneybird_resource_path_name(cls):
        if cls.moneybird_resource_path_name:
            return cls.moneybird_resource_path_name
        else:
            raise NotImplementedError

    version = models.IntegerField(
        null=True,
        blank=True,
        unique=True,
        help_text="This is the Moneybird version of the currently stored data and is used when looking for changes efficiently.",
    )

    @classmethod
    def get_moneybird_fields(cls):
        return super(MoneybirdSynchronizableResourceModel, cls).get_moneybird_fields() + ["version"]

    @classmethod
    def get_moneybird_readonly_fields(cls):
        return super(MoneybirdSynchronizableResourceModel, cls).get_moneybird_readonly_fields() + ["version"]

    @property
    def moneybird_resource_url(self):
        return (
            f"https://moneybird.com/{settings.MONEYBIRD_ADMINISTRATION_ID}/{self.get_moneybird_resource_path_name()}/{self.id}"
            if self.id
            else None
        )

    def get_absolute_url(self):
        return self.moneybird_resource_url


class MoneybirdNestedDataResourceModel(MoneybirdResourceModel):
    """Objects that dont exist independently but depend on another Model, like InvoiceDetailItems."""

    class Meta:
        abstract = True

    moneybird_nested_foreign_key = (
        None  # Should also be in the moneybird_data_fields # TODO maybe it shouldnt to prevent recursion errors
    )

    @classmethod
    def get_moneybird_nested_foreign_key(cls):
        return cls.moneybird_nested_foreign_key

    def get_moneybird_attr(self, field):
        if field == self.moneybird_nested_foreign_key:
            return getattr(self, field, None)
        return super(MoneybirdNestedDataResourceModel, self).get_moneybird_attr(field)


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


class InvoiceDetailItem(MoneybirdNestedDataResourceModel):
    class Meta:
        verbose_name = "invoice detail item"
        verbose_name_plural = "invoice detail items"

    moneybird_resource_name = "details"

    moneybird_data_fields = [
        "invoice_id",
        "tax_rate_id",
        "ledger_account_id",
        "project_id",
        "product_id",
        "amount",
        "amount_decimal",
        "description",
        "price",
        "period",
        "row_order",
        "total_price_excl_tax_with_discount",
        "total_price_excl_tax_with_discount_base",
    ]

    moneybird_nested_foreign_key = "invoice"

    invoice = models.ForeignKey(
        "SalesInvoice", related_name="details", null=False, blank=False, on_delete=CASCADE, db_constraint=False
    )  # db_constraint must be false to prevent integrity errors on sync, where objects are created without the parent yet existing

    tax_rate_id = models.CharField(blank=True, null=True, max_length=100)
    ledger_account_id = models.CharField(blank=True, null=True, max_length=100)
    project_id = models.CharField(blank=True, null=True, max_length=100)
    product_id = models.CharField(blank=True, null=True, max_length=100)

    amount = models.CharField(blank=True, null=True, max_length=10)
    amount_decimal = models.DecimalField(blank=True, null=True, max_digits=10, decimal_places=2)
    description = models.CharField(blank=True, null=True, max_length=1000)
    price = models.DecimalField(blank=True, null=True, max_digits=10, decimal_places=2)

    period = models.CharField(blank=True, null=True, max_length=100)  # TODO create a good period selector
    row_order = models.PositiveSmallIntegerField(null=True, blank=True)

    total_price_excl_tax_with_discount = models.DecimalField(blank=True, null=True, max_digits=10, decimal_places=2)
    total_price_excl_tax_with_discount_base = models.DecimalField(
        blank=True, null=True, max_digits=10, decimal_places=2
    )

    def __str__(self):
        return f"Invoice item {self.invoice}: {self.description} ({self.amount} {self.price})"


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
        "url",
        "original_sales_invoice_id",
        "payment_url",
        "payment_conditions",
        "payment_reference",
        "public_view_code",
        "sales_invoices_url",
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
        "paused",
        "paid_at",
        "sent_at",
        "payment_reference",
        "public_view_code",
        "original_sales_invoice_id",
        "url",
        "payment_url",
        "total_paid",
        "total_unpaid",
        "total_unpaid_base",
        "total_price_excl_tax",
        "total_price_excl_tax_base",
        "total_price_incl_tax",
        "total_price_incl_tax_base",
        "total_discount",
    ]
    moneybird_foreign_key_fields = ["contact"]
    moneybird_nested_data_fields = {
        "details": InvoiceDetailItem,
    }

    # TODO include recurring_sales_invoice_id

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
        (STATE_DRAFT, "Draft"),
        (STATE_OPEN, "Open"),
        (STATE_SCHEDULED, "Scheduled"),
        (STATE_PENDING_PAYMENT, "Pending payment"),
        (STATE_LATE, "Late"),
        (STATE_REMINDED, "Reminded"),
        (STATE_PAID, "Paid"),
        (STATE_UNCOLLECTIBLE, "Uncollectible"),
    )

    # TODO add help texts

    state = models.CharField(blank=True, null=True, choices=INVOICE_STATES, max_length=100)

    reference = models.CharField(blank=True, null=True, max_length=1000)
    invoice_date = models.DateField(
        blank=True, null=True, help_text="Will be set automatically when invoice is sent."
    )  # TODO fix serialization
    due_date = models.DateField(blank=True, null=True)  # TODO fix serialization
    # TODO fix due period

    discount = models.DecimalField(blank=True, null=True, max_digits=3, decimal_places=2)  # TODO check serialization

    paused = models.BooleanField(blank=False, null=False, default=False)  # Make readonly, add action
    paid_at = models.DateField(blank=True, null=True)  # TODO fix serialization
    sent_at = models.DateField(blank=True, null=True)  # TODO fix serialization

    original_sales_invoice = models.ForeignKey("self", null=True, blank=True, on_delete=CASCADE)
    payment_conditions = models.TextField(
        blank=True, null=True, help_text="Supports Moneybird tags in the form of {document.field}."
    )
    payment_reference = models.CharField(blank=True, null=True, max_length=100)
    public_view_code = models.CharField(blank=True, null=True, max_length=100)
    url = models.CharField(blank=True, null=True, max_length=1000)
    payment_url = models.CharField(blank=True, null=True, max_length=1000)

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
    prices_are_incl_tax = models.BooleanField(default=True, verbose_name="display prices incl. tax")

    # TODO pdf?

    @property
    def number_of_rows(self):
        return len(self.details.all())

    def __str__(self):
        if self.state == SalesInvoice.STATE_DRAFT:
            return f"Draft {self.draft_id}"
        else:
            return f"{self.invoice_id}"

    def send(self):
        pass
        # post to "pause"

    def pause(self):
        pass
        # post to "resume"

    def send_reminder(self):
        pass
        # post to "resume"1

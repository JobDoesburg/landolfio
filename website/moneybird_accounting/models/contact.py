from django.db import models

from django_countries.fields import CountryField
from django_iban.fields import IBANField

from moneybird_accounting.models.moneybird_resource import MoneybirdSynchronizableResourceModel


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

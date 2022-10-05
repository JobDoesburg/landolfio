from django.core.exceptions import ValidationError
from django.forms import models
from django.utils.translation import gettext_lazy as _

from accounting.models import Contact
from rental_customers.models import RegisteredRentalCustomer


class ContactForm(models.ModelForm):
    class Meta:
        model = Contact
        fields = [
            "first_name",
            "last_name",
            "company_name",
            "address_1",
            "address_2",
            "zip_code",
            "city",
            "country",
            "phone",
            "email",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["first_name"].required = True
        self.fields["last_name"].required = True
        self.fields["company_name"].required = False
        self.fields["company_name"].help_text = _("Optional")
        self.fields["address_1"].required = True
        self.fields["address_2"].required = False
        self.fields["address_2"].help_text = _("Optional")
        self.fields["zip_code"].required = True
        self.fields["city"].required = True
        self.fields["country"].required = True
        self.fields["phone"].required = True
        self.fields["email"].required = True


class RentalCustomerRegistrationForm(models.ModelForm):
    class Meta:
        model = RegisteredRentalCustomer
        fields = ["wants_sepa_mandate", "notes"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["wants_sepa_mandate"].initial = True
        self.fields["wants_sepa_mandate"].label = _("Pay by SEPA direct debit")
        self.fields["wants_sepa_mandate"].help_text = _(
            "With direct debit, all invoices will automatically be collected from your bank account."
        )
        self.fields["notes"].help_text = _(
            "If you received asset numbers, please enter them here."
        )

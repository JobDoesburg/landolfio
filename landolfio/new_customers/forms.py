import logging

from django.forms import Textarea, models
from django.utils.translation import gettext_lazy as _

from accounting.models import Contact
from new_customers.models import NewCustomer
from new_customers.services import detect_duplicate_contact


class NewContactForm(models.ModelForm):
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

    def save(self, commit=True):
        contact = super().save(commit=False)

        # Check if this contact already exists
        existing_contact = detect_duplicate_contact(contact)
        if existing_contact is not None:
            logging.info(
                f"Found existing contact while saving form, not creating a new one: {existing_contact}"
            )
            return existing_contact

        if commit:
            contact.save()
        return contact


class NewCustomerForm(models.ModelForm):
    class Meta:
        model = NewCustomer
        fields = [
            "wants_sepa_mandate",
            "description",
        ]
        widgets = {
            "description": Textarea(attrs={"rows": 4, "cols": 15}),
            "asset_numbers": Textarea(attrs={"rows": 2, "cols": 15}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["wants_sepa_mandate"].initial = True
        self.fields["wants_sepa_mandate"].label = _("Pay by SEPA direct debit")
        self.fields["wants_sepa_mandate"].help_text = _(
            "With direct debit, all invoices will automatically be collected from your bank account. You will receive "
            "an email to confirm the mandate via your bank by transferring an amount of €0,15 right after submitting."
        )
        self.fields["description"].label = _("Remarks")
        self.fields["description"].help_text = _("Optional room for additional notes.")

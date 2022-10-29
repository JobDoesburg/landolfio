from django.forms import models, Textarea
from django.utils.translation import gettext_lazy as _

from accounting.models import Contact
from inventory.services import find_existing_asset_from_description
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
        fields = [
            "instrument_numbers",
            "wants_sepa_mandate",
            "wants_reduced_liability",
            "affiliate_name",
            "notes",
        ]
        widgets = {
            "notes": Textarea(attrs={"rows": 4, "cols": 15}),
            "asset_numbers": Textarea(attrs={"rows": 2, "cols": 15}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["wants_sepa_mandate"].initial = True
        self.fields["wants_sepa_mandate"].label = _("Pay by SEPA direct debit")
        self.fields["wants_sepa_mandate"].help_text = _(
            "With direct debit, all invoices will automatically be collected from your bank account. You will receive an email to confirm the mandate via your bank by transferring an amount of €0,15 right after submitting."
        )
        self.fields["wants_reduced_liability"].initial = False
        self.fields["wants_reduced_liability"].label = _("Request reduced liability")
        self.fields["wants_reduced_liability"].help_text = _(
            "With reduced liability, your liability to material damages will be restricted to €50 per incident (with exception of bow hair, strings and bridges)."
        )

        self.fields["affiliate_name"].label = _("Contact person")
        self.fields["affiliate_name"].help_text = _(
            "If you received the instruments from one of our affiliate contact persons, please enter their name here."
        )
        self.fields["instrument_numbers"].label = _("Instrument numbers")
        self.fields["instrument_numbers"].help_text = _(
            "Please enter the instrument numbers of the instruments you received from us, separated with a comma."
        )

        self.fields["notes"].help_text = _("Optional room for additional notes.")

    def save(self, commit=True):
        instance = super().save(commit)
        if commit:
            detected_assets = find_existing_asset_from_description(
                instance.instrument_numbers
            )
            instance.assets.set(detected_assets, clear=True)
        return instance

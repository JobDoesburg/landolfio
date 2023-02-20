from django.forms import Textarea
from django.utils.translation import gettext_lazy as _

from inventory.services import find_existing_asset_from_description
from new_customers.forms import NewCustomerForm
from new_rental_customers.models import NewRentalCustomer


class NewRentalCustomerForm(NewCustomerForm):
    class Meta:
        model = NewRentalCustomer
        fields = [
            "instrument_numbers",
            "date_received",
            "wants_reduced_liability",
            "affiliate_name",
        ] + NewCustomerForm.Meta.fields
        widgets = NewCustomerForm.Meta.widgets | {
            "instrument_numbers": Textarea(attrs={"rows": 2, "cols": 15}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["date_received"].label = _("Date received")
        self.fields["date_received"].help_text = _(
            "When did you receive the instruments?"
        )
        self.fields["wants_reduced_liability"].initial = False
        self.fields["wants_reduced_liability"].label = _("Request reduced liability")
        self.fields["wants_reduced_liability"].help_text = _(
            "With reduced liability, your liability to material damages will be restricted to €50 per incident (with "
            "exception of bow hair, strings and bridges)."
        )

        self.fields["affiliate_name"].label = _("Contact person")
        self.fields["affiliate_name"].help_text = _(
            "If you received the instruments from one of our affiliate contact persons, please enter their name here."
        )
        self.fields["instrument_numbers"].label = _("Instrument numbers")
        self.fields["instrument_numbers"].help_text = _(
            "Please enter the instrument numbers of the instruments you received from us, separated with a comma."
        )

    def save(self, commit=True):
        instance = super().save(commit)
        if commit:
            detected_assets = find_existing_asset_from_description(
                instance.instrument_numbers
            )
            instance.assets.set(detected_assets, clear=True)
        return instance

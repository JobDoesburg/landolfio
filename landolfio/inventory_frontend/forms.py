from django import forms
from datetime import date
from django.utils.translation import gettext_lazy as _
from inventory.models.asset import Asset, AssetStates
from inventory.models.status_change import StatusChange
from accounting.models.contact import Contact


class HTML5DateInput(forms.DateInput):
    input_type = "date"

    def format_value(self, value):
        if value is None:
            return ""
        if hasattr(value, "strftime"):
            return value.strftime("%Y-%m-%d")
        return str(value)


class ColoredStatusSelect(forms.Select):
    def create_option(
        self, name, value, label, selected, index, subindex=None, attrs=None
    ):
        option = super().create_option(
            name, value, label, selected, index, subindex, attrs
        )

        # Add data-color attribute based on status value
        color = "primary"  # default
        if value == "":
            color = "light"
        elif value == "available":
            color = "success"
        elif value in ["issued_rent", "issued_loan", "issued_unprocessed"]:
            color = "warning"
        elif value in ["maintenance_in_house", "maintenance_external", "under_review"]:
            color = "info"
        elif value == "placeholder":
            color = "light"
        elif value == "to_be_delivered":
            color = "secondary"
        elif value == "sold":
            color = "secondary"
        elif value == "amortized":
            color = "dark"
        elif value == "unknown":
            color = "danger"

        option["attrs"]["data-color"] = color
        return option


class ContactAutocompleteWidget(forms.TextInput):
    def __init__(self, attrs=None):
        default_attrs = {"class": "form-control contact-autocomplete"}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)


class AssetForm(forms.ModelForm):
    start_date = forms.DateField(
        required=False,
        widget=HTML5DateInput(attrs={"class": "form-control"}),
        input_formats=["%Y-%m-%d"],
        localize=False,
    )

    class Meta:
        model = Asset
        fields = [
            "name",
            "category",
            "size",
            "collection",
            "location",
            "location_nr",
            "listing_price",
            "purchase_value_asset",
            "start_date",
            "is_margin_asset",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "category": forms.Select(attrs={"class": "form-control"}),
            "size": forms.Select(attrs={"class": "form-control"}),
            "collection": forms.Select(attrs={"class": "form-control"}),
            "location": forms.Select(attrs={"class": "form-control"}),
            "location_nr": forms.NumberInput(attrs={"class": "form-control"}),
            "listing_price": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
            "purchase_value_asset": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
            "is_margin_asset": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make certain fields optional
        self.fields["size"].required = False
        self.fields["location"].required = False
        self.fields["location_nr"].required = False
        self.fields["listing_price"].required = False
        self.fields["purchase_value_asset"].required = False
        self.fields["start_date"].required = False
        self.fields["is_margin_asset"].required = False

        # Set better initial values for create form (when instance doesn't exist yet)
        if not self.instance or not self.instance.pk:
            # Default start date to today for new assets
            self.fields["start_date"].initial = date.today()

            # Default is_margin_asset to False for new assets
            self.fields["is_margin_asset"].initial = False
        # For existing instances, the custom start_date field will automatically
        # handle the proper formatting with localize=False


class StatusChangeForm(forms.ModelForm):
    """Form for creating new status changes."""

    status_date = forms.DateField(
        required=True,
        widget=HTML5DateInput(attrs={"class": "form-control"}),
        input_formats=["%Y-%m-%d"],
        localize=False,
        label=_("Status Date"),
        initial=date.today,
    )

    new_status = forms.ChoiceField(
        choices=[("", _("No change"))] + list(AssetStates.choices),
        widget=ColoredStatusSelect(attrs={"class": "form-control status-select"}),
        label=_("New Status"),
        required=False,
    )

    contact_name = forms.CharField(
        required=False,
        widget=ContactAutocompleteWidget(
            attrs={"placeholder": _("Search for contact...")}
        ),
        label=_("Contact"),
        help_text=_("Associated Moneybird contact (optional)"),
    )

    contact_id = forms.CharField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = StatusChange
        fields = ["new_status", "status_date", "comments"]
        widgets = {
            "comments": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": _("Optional comments about this status change..."),
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        self.asset = kwargs.pop("asset", None)
        super().__init__(*args, **kwargs)

        # Set default status date to today and default to "no change"
        if not self.instance.pk:
            self.fields["status_date"].initial = date.today()
            # Default to "no change" instead of current status
            self.fields["new_status"].initial = ""
        else:
            # If editing existing status change, populate contact fields
            if self.instance.contact:
                self.fields["contact_name"].initial = str(self.instance.contact)
                self.fields["contact_id"].initial = self.instance.contact.id

    def save(self, commit=True):
        status_change = super().save(commit=False)
        if self.asset:
            status_change.asset = self.asset

        # Handle empty new_status (convert to None for "no change")
        new_status = self.cleaned_data.get("new_status")
        if new_status == "":
            status_change.new_status = None
        else:
            status_change.new_status = new_status

        # Handle contact assignment
        contact_id = self.cleaned_data.get("contact_id")
        if contact_id:
            try:
                contact = Contact.objects.get(id=contact_id)
                status_change.contact = contact
            except Contact.DoesNotExist:
                status_change.contact = None
        else:
            status_change.contact = None

        if commit:
            status_change.save()
        return status_change

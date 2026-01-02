from datetime import date

from django import forms
from django.utils.translation import gettext_lazy as _

from accounting.models.contact import Contact
from inventory.models.asset import Asset, AssetStates
from inventory.models.location import Location
from inventory.models.status_change import StatusChange


def get_locations_hierarchical():
    """Get locations sorted hierarchically by order field recursively."""
    all_locations = list(Location.objects.all())
    location_dict = {loc.id: loc for loc in all_locations}

    # Get ancestry chain order values for sorting
    def get_order_chain(location):
        """Returns tuple of order values from root to this location."""
        chain = []
        current = location
        while current:
            chain.insert(
                0, (current.order if current.order is not None else 999999, current.id)
            )
            if current.parent_id and not current.display_as_root:
                current = location_dict.get(current.parent_id)
            else:
                break
        return tuple(chain)

    # Sort all locations by their ancestry chain
    sorted_locations = sorted(all_locations, key=get_order_chain)
    return sorted_locations


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

        # Set hierarchical location ordering
        ordered_locations = get_locations_hierarchical()
        # Convert list to queryset with preserved order
        if ordered_locations:
            location_ids = [loc.id for loc in ordered_locations]
            # Use Case/When to preserve the order
            from django.db.models import Case, When

            preserved_order = Case(
                *[When(pk=pk, then=pos) for pos, pk in enumerate(location_ids)]
            )
            self.fields["location"].queryset = Location.objects.filter(
                id__in=location_ids
            ).order_by(preserved_order)
        else:
            self.fields["location"].queryset = Location.objects.none()

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
                    "rows": 3,
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


class BulkStatusChangeForm(forms.Form):
    """Form for creating status changes for multiple assets at once."""

    assets = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control asset-autocomplete-bulk",
                "placeholder": _("Start typing asset names..."),
            }
        ),
        label=_("Assets"),
        help_text=_("Select multiple assets using autocomplete"),
    )

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

    comments = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 5,
                "placeholder": _("Optional comments about this status change..."),
            }
        ),
        label=_("Comments"),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["status_date"].initial = date.today()

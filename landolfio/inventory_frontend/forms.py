from django import forms
from datetime import date
from django.utils.translation import gettext_lazy as _
from inventory.models.asset import Asset, AssetStates


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
        if value == "available":
            color = "success"
        elif value in ["issued_rent", "issued_loan", "issued_unprocessed"]:
            color = "warning"
        elif value in ["maintenance_in_house", "maintenance_external", "under_review"]:
            color = "info"
        elif value in ["placeholder", "to_be_delivered"]:
            color = "secondary"
        elif value in ["sold", "amortized"]:
            color = "dark"
        elif value == "unknown":
            color = "danger"

        option["attrs"]["data-color"] = color
        return option


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
            "local_status",
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
            "local_status": ColoredStatusSelect(
                attrs={"class": "form-control status-select"}
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
            # Default local status to placeholder for new assets
            self.fields["local_status"].initial = AssetStates.PLACEHOLDER

            # Default start date to today for new assets
            self.fields["start_date"].initial = date.today()

            # Default is_margin_asset to False for new assets
            self.fields["is_margin_asset"].initial = False
        # For existing instances, the custom start_date field will automatically
        # handle the proper formatting with localize=False

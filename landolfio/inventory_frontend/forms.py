from django import forms
from inventory.models.asset import Asset


class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = [
            'name', 'category', 'size', 'collection',
            'location', 'location_nr', 'listing_price', 'local_status'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'size': forms.Select(attrs={'class': 'form-control'}),
            'collection': forms.Select(attrs={'class': 'form-control'}),
            'location': forms.Select(attrs={'class': 'form-control'}),
            'location_nr': forms.NumberInput(attrs={'class': 'form-control'}),
            'listing_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'local_status': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make certain fields optional
        self.fields['size'].required = False
        self.fields['location'].required = False
        self.fields['location_nr'].required = False
        self.fields['listing_price'].required = False

from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit
from django import forms

from .models import BillingAddress, ShippingAddress


class BillingAddressForm(forms.ModelForm):
    class Meta:
        model = BillingAddress
        fields = ['attention', 'country_region', 'street_1', 'street_2', 'city', 'state', 'zip_code', 'phone', 'fax']

        labels = {
            'attention': 'Attention:',
            'country_region': 'Country:',
            'street_1': 'Street Address 1:',
            'street_2': 'Street Address 2:',
            'city': 'City:',
            'state': 'State/Province:',
            'zip_code': 'ZIP/Postal Code:',
            'phone': 'Phone:',
            'fax': 'Fax:',
        }

        widgets = {
            'attention': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Attention', 'name': 'billing_attention'}),
            'country_region': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Country', 'name': 'billing_country_region'}),
            'street_1': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Street Address 1', 'name': 'billing_street_1'}),
            'street_2': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Street Address 2', 'name': 'billing_street_2'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City', 'name': 'billing_city'}),
            'state': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'State/Province', 'name': 'billing_state'}),
            'zip_code': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'ZIP/Postal Code', 'name': 'billing_zip_code'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone', 'name': 'billing_phone'}),
            'fax': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Fax', 'name': 'billing_fax'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'row g-3'
        self.helper.layout = Layout(
            Row(
                Column('attention', css_class='form-group col-md-12 mb-3'),
            ),
            Row(
                Column('country_region', css_class='form-group col-md-6 mb-3'),
                Column('phone', css_class='form-group col-md-6 mb-3'),
                css_class='row'
            ),
            Row(
                Column('street_1', css_class='form-group col-md-12 mb-3'),
            ),
            Row(
                Column('street_2', css_class='form-group col-md-12 mb-3'),
            ),
            Row(
                Column('city', css_class='form-group col-md-6 mb-3'),
                Column('state', css_class='form-group col-md-6 mb-3'),
                css_class='row'
            ),
            Row(
                Column('zip_code', css_class='form-group col-md-6 mb-3'),
                Column('fax', css_class='form-group col-md-6 mb-3'),
                css_class='row'
            ),
            FormActions(
                Submit('submit', 'Submit', css_class='btn btn-primary')
            )
        )


class ShippingAddressForm(forms.ModelForm):
    class Meta:
        model = ShippingAddress
        fields = ['attention', 'country_region', 'street_1', 'street_2', 'city', 'state', 'zip_code', 'phone', 'fax']

        labels = {
            'attention': 'Attention:',
            'country_region': 'Country:',
            'street_1': 'Street Address 1:',
            'street_2': 'Street Address 2:',
            'city': 'City:',
            'state': 'State/Province:',
            'zip_code': 'ZIP/Postal Code:',
            'phone': 'Phone:',
            'fax': 'Fax:',
        }

        widgets = {
            'attention': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Attention', 'name': 'shipping_attention'}),
            'country_region': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Country', 'name': 'shipping_country_region'}),
            'street_1': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Street Address 1', 'name': 'shipping_street_1'}),
            'street_2': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Street Address 2', 'name': 'shipping_street_2'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City', 'name': 'shipping_city'}),
            'state': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'State/Province', 'name': 'shipping_state'}),
            'zip_code': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'ZIP/Postal Code', 'name': 'shipping_zip_code'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone', 'name': 'shipping_phone'}),
            'fax': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Fax', 'name': 'shipping_fax'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'row g-3'  # Bootstrap spacing for form rows
        self.helper.layout = Layout(
            Row(
                Column('attention', css_class='form-group col-md-12 mb-3'),
            ),
            Row(
                Column('country_region', css_class='form-group col-md-6 mb-3'),
                Column('phone', css_class='form-group col-md-6 mb-3'),
                css_class='row'
            ),
            Row(
                Column('street_1', css_class='form-group col-md-12 mb-3'),
                css_class='row mt-3'
            ),
            Row(
                Column('street_2', css_class='form-group col-md-12 mb-3'),
                css_class='row mt-3'

            ),
            Row(
                Column('city', css_class='form-group col-md-6 mb-3'),
                Column('state', css_class='form-group col-md-6 mb-3'),
                css_class='row'
            ),
            Row(
                Column('zip_code', css_class='form-group col-md-6 mb-3'),
                Column('fax', css_class='form-group col-md-6 mb-3'),
                css_class='row'
            ),
            FormActions(
                Submit('submit', 'Submit', css_class='btn btn-primary')
            )
        )

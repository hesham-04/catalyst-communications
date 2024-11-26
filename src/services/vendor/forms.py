from crispy_forms.bootstrap import FormActions
from django import forms
from crispy_forms.layout import HTML
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Div, Submit
from .models import Vendor


class VendorForm(forms.ModelForm):
    class Meta:
        model = Vendor
        fields = [
            'name', 'address', 'iban', 'email', 'phone',
            'registration_number', 'vat_number', 'website',
            'currency'
        ]

        labels = {
            'name': 'Vendor Name:',
            'address': 'Address:',
            'iban': 'IBAN:',
            'email': 'Email:',
            'phone': 'Phone:',
            'registration_number': 'Registration Number:',
            'vat_number': 'VAT Number:',
            'website': 'Website:',
            'currency': 'Currency:',
        }

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Vendor Name'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Address'}),
            'iban': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'IBAN'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone'}),
            'registration_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Registration Number'}),
            'vat_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'VAT Number'}),
            'website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Website'}),
            'currency': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'row g-3'  # Bootstrap spacing for form rows
        self.helper.layout = Layout(
            Row(
                Column('name', css_class='form-group col-md-12 mb-3'),
            ),
            Row(
                Column('address', css_class='form-group col-md-12 mb-3'),
            ),
            Row(
                HTML('<h4 class="m-2 ms-0">Contact Details</h4>'),
                css_class='col-12'
            ),
            Row(
                Column('email', css_class='form-group col-md-6 mb-3'),
                Column('phone', css_class='form-group col-md-6 mb-3'),
                css_class='row'
            ),
            Row(
                HTML('<h4 class="m-2 ms-0">Banking and Tax Information</h4>'),
                css_class='col-12'
            ),
            Row(
                Column('iban', css_class='form-group col-md-6 mb-3'),
                Column('registration_number', css_class='form-group col-md-6 mb-3'),
                css_class='row'
            ),
            Row(
                Column('vat_number', css_class='form-group col-md-6 mb-3'),
                Column('website', css_class='form-group col-md-6 mb-3'),
                css_class='row'
            ),
            Row(
                Column('currency', css_class='form-group col-md-12 mb-3'),
            ),
            FormActions(
                Submit('submit', 'Submit', css_class='btn btn-primary')
            )
        )

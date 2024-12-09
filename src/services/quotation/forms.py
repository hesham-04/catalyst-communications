from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column
from django import forms

from .models import Quotation, QuotationItem


class QuotationForm(forms.ModelForm):
    class Meta:
        model = Quotation
        fields = [
            'client_name', 'company_name', 'phone', 'address', 'date',
            'subject', 'notes', 'validity_date', 'letterhead', 'tax', 'project'
        ]

        widgets = {
            'client_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Client Name'}),
            'company_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company Name'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Address'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subject'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Notes', 'rows': 3}),
            'validity_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'letterhead': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'tax': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'project': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'row g-3'
        self.helper.layout = Layout(
            Row(
                Column('client_name', css_class='form-group col-md-6 mb-3'),
                Column('company_name', css_class='form-group col-md-6 mb-3'),
                css_class='row'
            ),
            Row(
                Column('phone', css_class='form-group col-md-6 mb-3'),
                Column('address', css_class='form-group col-md-6 mb-3'),
                css_class='row'
            ),
            Row(
                Column('date', css_class='form-group col-md-6 mb-3'),
                Column('validity_date', css_class='form-group col-md-6 mb-3'),
                css_class='row'
            ),
            Row(
                Column('subject', css_class='form-group col-md-6 mb-3'),
                Column('notes', css_class='form-group col-md-6 mb-3'),
                css_class='row'
            ),
            Row(
                Column('letterhead', css_class='form-check mt-4 ms-2'),
                Column('tax', css_class='form-check mt-4 ms-2'),
                css_class='row'
            ),
            Row(
                Column('project', css_class='form-group col-md-6 mb-3'),
                css_class='row'
            )
        )


class QuotationItemForm(forms.ModelForm):
    class Meta:
        model = QuotationItem
        fields = ['item_name', 'description', 'quantity', 'rate', 'tax']

        widgets = {
            'item_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Item Name'}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Description'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Quantity'}),
            'rate': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Rate'}),
            'tax': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Tax'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'row g-3'
        self.helper.layout = Layout(
            Row(
                Column('item_name', css_class='form-group col-md-6 mb-3'),
                Column('description', css_class='form-group col-md-6 mb-3'),
                css_class='row'
            ),
            Row(
                Column('quantity', css_class='form-group col-md-6 mb-3'),
                Column('rate', css_class='form-group col-md-6 mb-3'),
                css_class='row'
            ),
            Row(
                Column('tax', css_class='form-group col-md-6 mb-3'),
                css_class='row'
            )
        )



#
# class QuotationForm(forms.ModelForm):
#     class Meta:
#         model = Quotation
#         fields = ['client_name', 'company_name', 'phone', 'address', 'subject', 'notes', 'tax']
#
#
#
# class QuotationItemForm(forms.ModelForm):
#     class Meta:
#         model = QuotationItem
#         fields = ['item_name', 'description', 'quantity', 'rate']
#
#         widgets = {
#             'item_name': forms.TextInput(attrs={
#                 'required': True,  # HTML required attribute
#                 'placeholder': 'Enter item name',
#             }),
#             'description': forms.Textarea(attrs={
#                 'required': True,
#                 'placeholder': 'Enter description',
#                 'rows': 3,
#             }),
#             'quantity': forms.NumberInput(attrs={
#                 'required': True,
#                 'min': 1,
#                 'placeholder': 'Enter quantity',
#             }),
#             'rate': forms.NumberInput(attrs={
#                 'required': True,
#                 'min': 0,
#                 'placeholder': 'Enter the rate',
#             }),
#         }

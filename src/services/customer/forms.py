from crispy_forms.bootstrap import FormActions
from django import forms
from crispy_forms.layout import HTML
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Div, Submit
from .models import Customer


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = [
            'salutation', 'first_name', 'last_name', 'company_name',
            'customer_type', 'email', 'phone', 'work_phone', 'mobile', 'other_details',
            'currency', 'payment_due_period', 'company_id'
        ]

        labels = {
            'customer_type': 'Customer Type:',
            'company_name': 'Company Name:',
            'email': 'Email:',
            'phone': 'Phone:',
            'work_phone': 'Work Phone:',
            'mobile': 'Mobile:',
        }

        widgets = {
            'salutation': forms.Select(attrs={'class': 'form-select'}),
            'payment_due_period': forms.Select(attrs={'class': 'form-select'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'company_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company Name'}),
            'customer_type': forms.Select(attrs={'class': 'form-select'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone'}),
            'work_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Work Phone'}),
            'mobile': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mobile'}),
            'company_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company ID'}),
            'other_details': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Other Details'}),
            'currency': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Mark all fields as required
        for field_name, field in self.fields.items():
            field.required = True

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'row g-3'  # Bootstrap spacing for form rows
        self.helper.layout = Layout(
            Row(
                Column('customer_type', css_class='form-group mb-3'),
            ),
            Row(
                Column('company_name', css_class='col-md-12 mb-3'),
                css_class='row'
            ),
            Row(
                HTML('<h4 class="m-2 ms-0">Primary Contact</h4>'),
                css_class='col-12'
            ),
            Row(
                Column('salutation', css_class='form-group col-md-4 mb-3'),
                Column('first_name', css_class='form-group col-md-4 mb-3'),
                Column('last_name', css_class='form-group col-md-4 mb-3'),
                css_class='row'
            ),
            Row(
                Column('email', css_class='form-group col-md-12 mb-3'),
                css_class='row'
            ),
            Row(
                Column('phone', css_class='form-group col-md-4 mb-3'),
                Column('work_phone', css_class='form-group col-md-4 mb-3'),
                Column('mobile', css_class='form-group col-md-4 mb-3'),
                css_class='row'
            ),
            Row(
                Column('other_details', css_class='form-group col-md-12 mb-3'),
                css_class='row'
            ),
            Row(
                Column('currency', css_class='form-group col-md-6 mb-3'),
                Column('company_id', css_class='form-group col-md-6 mb-3'),
                css_class='row'
            ),
            Row(
                Column('payment_due_period', css_class='form-group col-md-12 mb-3'),
                css_class='row'
            ),
            FormActions(
                Submit('submit', 'Submit', css_class='btn btn-primary')
            )
        )

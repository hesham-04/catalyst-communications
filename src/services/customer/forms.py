from django import forms

from .models import Customer


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = [
            'salutation', 'first_name', 'last_name', 'company_name', 'display_name',
            'customer_type', 'email', 'phone', 'work_phone', 'mobile', 'other_details', 'currency'
        ]
        widgets = {
            'salutation': forms.Select(attrs={'class': 'form-select'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'company_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company Name'}),
            'display_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Display Name'}),
            'customer_type': forms.Select(attrs={'class': 'form-select'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone'}),
            'work_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Work Phone'}),
            'mobile': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mobile'}),
            'other_details': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Other Details'}),
            'currency': forms.Select(attrs={'class': 'form-select'}),
        }

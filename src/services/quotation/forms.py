from django import forms
from .models import Quotation, QuotationItem

class QuotationForm(forms.ModelForm):
    class Meta:
        model = Quotation
        fields = ['client_name', 'company_name', 'phone', 'address', 'subject', 'notes', 'percent_tax']



class QuotationItemForm(forms.ModelForm):
    class Meta:
        model = QuotationItem
        fields = ['item_name', 'description', 'quantity', 'rate']

        widgets = {
            'item_name': forms.TextInput(attrs={
                'required': True,  # HTML required attribute
                'placeholder': 'Enter item name',
            }),
            'description': forms.Textarea(attrs={
                'required': True,
                'placeholder': 'Enter description',
                'rows': 3,
            }),
            'quantity': forms.NumberInput(attrs={
                'required': True,
                'min': 1,
                'placeholder': 'Enter quantity',
            }),
            'rate': forms.NumberInput(attrs={
                'required': True,
                'min': 0,
                'placeholder': 'Enter the rate',
            }),
        }

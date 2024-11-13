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

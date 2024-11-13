from django import forms
from .models import Invoice, InvoiceItem

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['client_name', 'company_name', 'phone',  'address', 'percent_tax', 'subject', 'notes']


class InvoiceItemForm(forms.ModelForm):
    class Meta:
        model = InvoiceItem
        fields = ['item_name', 'description', 'quantity', 'rate']

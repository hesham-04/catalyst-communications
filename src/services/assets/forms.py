from django import forms
from .models import CashInHand, AccountBalance

class CashInHandForm(forms.ModelForm):
    class Meta:
        model = CashInHand
        fields = ['balance']
        widgets = {
            'balance': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter balance'}),
        }


class AccountBalanceForm(forms.ModelForm):
    class Meta:
        model = AccountBalance
        fields = ['balance']
        widgets = {
            'balance': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter new balance'}),
        }

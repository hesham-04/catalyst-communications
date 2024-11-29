from django import forms
from .models import CashInHand, AccountBalance

class CashInHandForm(forms.Form):
    balance = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter balance'}),
        required=True
    )
    source = forms.ModelChoiceField(
        queryset=AccountBalance.objects.all(),
        label="Select Source",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    reason = forms.CharField(
        required=True,
        label="Reason",
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Reason'}),
    )


class AccountBalanceForm(forms.ModelForm):
    class Meta:
        model = AccountBalance
        fields = ['balance']
        widgets = {
            'balance': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter new balance'}),
        }

from django import forms
from .models import CashInHand, AccountBalance


class CashInHandForm(forms.Form):
    balance = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "Enter balance"}
        ),
        required=True,
    )
    source = forms.ModelChoiceField(
        queryset=AccountBalance.objects.all(),
        label="Select Source",
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    reason = forms.CharField(
        required=True,
        label="Reason",
        max_length=100,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Reason"}
        ),
    )


class AccountBalanceForm(forms.ModelForm):
    class Meta:
        model = AccountBalance
        fields = ["balance"]
        widgets = {
            "balance": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Enter starting balance"}
            ),
        }


class AddBalance(forms.Form):
    balance = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "Enter balance"}
        ),
        required=True,
    )
    source = forms.CharField(
        required=True,
        label="Source",
        max_length=100,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Source"}
        ),
    )


class TransferForm(forms.Form):
    destination = forms.ModelChoiceField(
        queryset=AccountBalance.objects.none(),  # Set an empty queryset initially
        label="Select Destination",
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "Enter amount"}
        ),
        required=True,
    )
    reason = forms.CharField(
        required=True,
        label="Reason",
        max_length=100,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Reason"})
    )

    def __init__(self, *args, current_account=None, **kwargs):
        super().__init__(*args, **kwargs)
        if current_account:
            self.fields["destination"].queryset = AccountBalance.objects.exclude(pk=current_account.pk)

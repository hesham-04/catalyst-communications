from django import forms
from django.core.exceptions import ValidationError
from .models import Lender, Loan, LoanReturn, MiscLoan
from ..assets.models import AccountBalance


class LoanForm(forms.ModelForm):

    lender = forms.ModelChoiceField(
        queryset=Lender.objects.all(),
        label="Select Lender",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    loan_amount = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        label="Loan Amount",
        widget=forms.NumberInput(
            attrs={'class': 'form-control', 'placeholder': 'Enter loan amount'}
        )
    )

    interest_rate = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        label="Interest Rate",
        widget=forms.NumberInput(
            attrs={'class': 'form-control', 'placeholder': 'Flat Interest Rate %'}
        )
    )



    reason = forms.CharField(
        label="Reason",
        max_length=255,
        required=True,
        widget=forms.TextInput(
            attrs={'class': 'form-control'}
        )
    )
    due_date = forms.DateField(
        label="Due Date",
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )

    class Meta:
        model = Loan
        fields = ['lender', 'loan_amount', 'reason', 'interest_rate', 'due_date']


class LoanReturnForm(forms.ModelForm):
    class Meta:
        model = LoanReturn
        fields = ['return_amount', 'return_date', 'remarks',]

        widgets = {
            'return_amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter return amount'}),
            'return_date': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                    'class': 'form-control',
                    'placeholder': 'Select date and time',
                }
            ),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Optional remarks', 'rows': 3}),
        }



class MiscLoanForm(forms.ModelForm):
    lender = forms.ModelChoiceField(
        queryset=Lender.objects.all(),
        label="Select Lender",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    loan_amount = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        label="Loan Amount",
        widget=forms.NumberInput(
            attrs={'class': 'form-control', 'placeholder': 'Enter loan amount'}
        )
    )
    interest_rate = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        label="Interest Rate",
        widget=forms.NumberInput(
            attrs={'class': 'form-control', 'placeholder': 'Flat Interest Rate %'}
        )
    )
    reason = forms.CharField(
        label="Reason",
        max_length=255,
        required=True,
        widget=forms.TextInput(
            attrs={'class': 'form-control'}
        )
    )
    due_date = forms.DateField(
        label="Due Date",
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    destination = forms.ModelChoiceField(
        queryset=AccountBalance.objects.all(),
        label="Destination Account",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = MiscLoan
        fields = ['lender', 'loan_amount', 'interest_rate', 'reason', 'due_date', 'destination']


class MiscLoanReturnForm(forms.Form):
    return_amount = forms.DecimalField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter return amount'
        }),
        label="Return Amount",
        max_digits=10,
        decimal_places=2,
    )
    return_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control',
            'placeholder': 'Select date and time',
        }),
        label="Return Date",
    )

    source = forms.ModelChoiceField(
        queryset=AccountBalance.objects.all(),
        label="Source Account",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    remarks = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Optional remarks',
            'rows': 3,
        }),
        label="Remarks",
        required=False,
    )
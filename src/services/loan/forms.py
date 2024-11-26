from django import forms
from django.core.exceptions import ValidationError
from .models import Lender, Loan, LoanReturn


class LoanForm(forms.ModelForm):
    DESTINATION_CHOICES = [
        ('CASH', 'Project Cash'),
        ('ACC', 'Project Account'),
    ]
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
    destination = forms.ChoiceField(
        choices=DESTINATION_CHOICES,
        label="Destination",
        widget=forms.Select(
        attrs={'class': 'form-control', 'placeholder': 'Enter destination'}
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
        fields = ['lender', 'loan_amount', 'destination', 'reason', 'due_date']


class LoanReturnForm(forms.ModelForm):
    class Meta:
        model = LoanReturn
        fields = ['return_amount', 'return_date', 'remarks', 'source']

        widgets = {
            'return_amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter return amount'}),
            'return_date': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                    'class': 'form-control',
                    'placeholder': 'Select date and time',
                }
            ),
            'source': forms.Select(attrs={'class': 'form-control'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Optional remarks', 'rows': 3}),
        }
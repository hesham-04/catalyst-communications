from django import forms
from django.utils.timezone import now

from .models import Expense, ExpenseCategory, JournalExpense
from ..assets.models import AccountBalance
from datetime import datetime


class ExpenseForm(forms.ModelForm):
    created_at = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"})
    )

    class Meta:
        model = Expense
        fields = ["description", "amount", "budget_source", "category", "vendor", "created_at"]
        widgets = {
            "description": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter description"}),
            "amount": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Enter amount", "required": True}),
            "category": forms.Select(attrs={"class": "form-control", "required": True}),
            "vendor": forms.Select(attrs={"class": "form-control", "required": True}),
        }


class ExpenseCategoryForm(forms.ModelForm):
    class Meta:
        model = ExpenseCategory
        fields = ["name"]

    def __init__(self, *args, **kwargs):
        super(ExpenseCategoryForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})


class ExpensePaymentForm(forms.Form):
    SOURCE_CHOICES = [
        ("CASH", "Project Cash"),
        ("ACC", "Project Account"),
    ]

    source = forms.ChoiceField(
        choices=SOURCE_CHOICES, widget=forms.Select(attrs={"class": "form-control"})
    )
    remarks = forms.CharField(
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 3})
    )


class JournalExpenseForm(forms.ModelForm):
    BUDGET_SOURCE_CHOICES = [
        ("CASH", "Cash in Hand"),
        ("ACC", "Account Balance"),
    ]

    budget_source = forms.ChoiceField(
        choices=BUDGET_SOURCE_CHOICES,
        required=True,
        label="Budget Source",
        initial="cash_in_hand",
    )
    account = forms.ModelChoiceField(
        queryset=AccountBalance.objects,
        required=False,
        label="Select Account (if applicable)",
    )
    created_at = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"}),
        initial=now,
    )

    class Meta:
        model = JournalExpense
        fields = [
            "description",
            "amount",
            "budget_source",
            "account",
            "category",
            "vendor",
            "created_at",
        ]
        widgets = {
            "description": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter description"}),
            "amount": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Enter amount"}),
            "category": forms.Select(attrs={"class": "form-control", "required": True}),
            "vendor": forms.Select(attrs={"class": "form-control", "required": True}),
        }

    def clean(self):
        cleaned_data = super().clean()
        budget_source = cleaned_data.get("budget_source")

        if budget_source == "ACC":
            account = cleaned_data.get("account")
            if not account:
                raise forms.ValidationError(
                    "An account must be selected when 'Account Balance' is chosen."
                )

            account_pk = account.pk
            cleaned_data["account_pk"] = account_pk

        return cleaned_data


class DateRangeForm(forms.Form):
    start_date = forms.DateField(
        widget=forms.DateInput(
            attrs={
                "class": "form-control",
                "id": "startDate",
                "type": "date",
                "required": True,
            }
        ),
        label="Starting Date",
    )
    end_date = forms.DateField(
        widget=forms.DateInput(
            attrs={
                "class": "form-control",
                "id": "endDate",
                "type": "date",
                "required": True,
            }
        ),
        label="Ending Date",
    )


class YearForm(forms.Form):
    current_year = datetime.now().year
    year_choices = [(year, str(year)) for year in range(2019, current_year + 1)]

    year = forms.ChoiceField(
        choices=year_choices,
        initial=current_year,
        widget=forms.Select(attrs={"class": "form-control", "id": "year", "required": True}),
        label="Select Year",
    )

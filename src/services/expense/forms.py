from django import forms

from .models import Expense, ExpenseCategory, JournalExpense
from ..assets.models import AccountBalance
from ..project.models import Project


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['description', 'amount', 'budget_source', 'category', 'vendor']


class ExpenseFormCreate(forms.ModelForm):
    project = forms.ModelChoiceField(
        queryset=Project.objects.all(),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Select Project"
    )

    class Meta:
        model = Expense
        fields = ['project', 'description', 'amount', 'budget_source', 'category', 'vendor']
        widgets = {
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Expense description'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Amount',
                'step': '0.01'
            }),
            'budget_source': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'vendor': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise forms.ValidationError("Amount must be a positive value.")
        return amount


class ExpenseCategoryForm(forms.ModelForm):
    class Meta:
        model = ExpenseCategory
        fields = ['name']

    def __init__(self, *args, **kwargs):
        super(ExpenseCategoryForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

class ExpensePaymentForm(forms.Form):
    SOURCE_CHOICES = [
        ('CASH', 'Project Cash'),
        ('ACC', 'Project Account'),
    ]

    source = forms.ChoiceField(
        choices=SOURCE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    remarks = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))




class JournalExpenseForm(forms.ModelForm):
    BUDGET_SOURCE_CHOICES = [
        ('CASH', 'Cash in Hand'),
        ('ACC', 'Account Balance'),
    ]

    budget_source = forms.ChoiceField(
        choices=BUDGET_SOURCE_CHOICES,
        required=True,
        label="Budget Source",
        initial='cash_in_hand',
    )
    account = forms.ModelChoiceField(
        queryset=AccountBalance.objects.all(),
        required=False,
        label="Select Account (if applicable)"
    )

    class Meta:
        model = JournalExpense
        fields = ['description', 'amount', 'budget_source', 'account', 'category', 'vendor']
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter description'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter amount'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'vendor': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        budget_source = cleaned_data.get('budget_source')

        if budget_source == 'ACC':
            account = cleaned_data.get('account')
            if not account:
                raise forms.ValidationError("An account must be selected when 'Account Balance' is chosen.")

            account_pk = account.pk
            cleaned_data['account_pk'] = account_pk

        return cleaned_data

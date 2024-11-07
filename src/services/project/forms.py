from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Div, Submit, HTML
from django import forms
from .models import Project


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['project_name', 'description', 'customer']

        labels = {
            'project_name': 'Project Name:',
            'description': 'Project Description:',
            'customer': 'Customer:',
        }

        widgets = {
            'project_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter project name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Describe the project'}),
            'customer': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'row g-3'
        self.helper.layout = Layout(
            Row(
                Column('project_name', css_class='form-group col-md-12 mb-3'),
            ),
            Row(
                Column('description', css_class='form-group col-md-12 mb-3'),
            ),
            Row(
                Column('customer', css_class='form-group col-md-12 mb-3'),

            ),

            FormActions(
                Submit('submit', 'Create Project', css_class='btn btn-primary')
            )
        )


class AddBudgetForm(forms.Form):
    SOURCE_CHOICES = [
        ('CASH', 'Cash in Hand'),
        ('ACC', 'Account'),
        ('CLIENT', 'Client Funds'),
    ]

    amount = forms.DecimalField(max_digits=12, decimal_places=2, label="Amount")
    source = forms.ChoiceField(choices=SOURCE_CHOICES, label="Budget Source")
    transaction_type = forms.ChoiceField(
        choices=[('CREDIT', 'Credit')],
        initial='CREDIT',
        widget=forms.HiddenInput(),
        label="Transaction Type"
    )

    # Add any widget attributes for styling
    amount.widget.attrs.update({'class': 'form-control', 'placeholder': 'Enter amount'})
    source.widget.attrs.update({'class': 'form-control'})




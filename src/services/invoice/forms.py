from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column
from django import forms

from .models import Invoice, InvoiceItem
from ..assets.models import AccountBalance


class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice

        fields = [
            "client_name",
            "company_name",
            "phone",
            "address",
            "due_date",
            "subject",
            "notes",
            "letterhead",
        ]

        widgets = {
            "client_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Client Name",
                    "required": True,
                }
            ),
            "company_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Company Name",
                    "required": True,
                }
            ),
            "phone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Phone Number",
                    "required": True,
                }
            ),
            "address": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Address",
                    "required": True,
                }
            ),
            "due_date": forms.DateInput(
                attrs={"class": "form-control", "type": "Date", "required": True}
            ),
            "subject": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Subject",
                    "required": True,
                }
            ),
            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Notes",
                    "rows": 6,
                    "required": True,
                }
            ),
            "letterhead": forms.CheckboxInput(
                attrs={"class": "form-check-input", "required": True}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_class = "row g-3"
        self.helper.layout = Layout(
            Row(
                Column("client_name", css_class="form-group col-md-6 mb-3"),
                Column("company_name", css_class="form-group col-md-6 mb-3"),
                css_class="row",
            ),
            Row(
                Column("phone", css_class="form-group col-md-6 mb-3"),
                Column("address", css_class="form-group col-md-6 mb-3"),
                css_class="row",
            ),
            Row(
                Column("subject", css_class="form-group col-md-6 mb-3"),
                Column("notes", css_class="form-group col-md-6 mb-3"),
                css_class="row",
            ),
            Row(
                Column("due_date", css_class="form-group col-md-6 mb-3"),
                Column("letterhead", css_class="form-check mt-4  ms-2"),
                css_class="row",
            ),
        )


class InvoiceItemForm(forms.ModelForm):
    class Meta:
        model = InvoiceItem
        fields = ["item_name", "description", "quantity", "rate", "tax"]

        # Commented Out because when applied:
        # 1. We have to Use {% crispy formset %}
        # 2. Which then renders  a separate form within the initial <form>

        widgets = {
            "item_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Item name",
                    "required": True,
                }
            ),
            "description": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Description",
                    "required": True,
                }
            ),
            "quantity": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Item Quantity",
                    "required": True,
                }
            ),
            "rate": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Item Rate",
                    "required": True,
                }
            ),
            "tax": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Item Tax",
                    "required": False,
                }
            ),
        }


class TransferFundsForm(forms.Form):
    account = forms.ModelChoiceField(
        queryset=AccountBalance.objects,
        required=True,
        label="Select Bank Account",
    )

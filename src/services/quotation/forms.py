from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column
from django import forms

from .models import Quotation, QuotationGeneral, ItemGeneral
from .models import QuotationItem


class QuotationForm(forms.ModelForm):
    class Meta:
        model = Quotation
        fields = [
            "client_name",
            "company_name",
            "phone",
            "email",
            "address",
            "subject",
            "notes",
            "letterhead",
            "due_date",
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
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Email",
                }
            ),
            "address": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Address",
                    "required": True,
                }
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
                    "required": True,
                }
            ),
            "letterhead": forms.CheckboxInput(
                attrs={"class": "form-check-input", "required": True}
            ),
            "due_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date", "required": True}
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
                Column("email", css_class="form-group col-md-12 mb-3"),
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


class QuotationItemForm(forms.ModelForm):
    class Meta:
        model = QuotationItem
        fields = ["item_name", "description", "quantity", "rate", "tax"]

        widgets = {
            "item_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Item Name",
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
                    "placeholder": "Quantity",
                    "required": True,
                }
            ),
            "rate": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Rate", "required": True}
            ),
            "tax": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Tax (%)",
                    "required": False,
                    "maxlength": 3,
                    "step": "0.1",
                }
            ),
        }

    def save(self, *args, **kwargs):
        instance = super().save(commit=False)
        # Calculate amount including tax
        instance.save()  # Automatically updates the amount and total
        return instance


class QuotationUpdateForm(forms.ModelForm):
    class Meta:
        model = Quotation
        fields = [
            "client_name",
            "company_name",
            "phone",
            "date",
            "quotation_number",
            "email",
            "address",
            "subject",
            "notes",
            "letterhead",
            "due_date",
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
                }
            ),
            "date": forms.DateInput(
                attrs={"class": "form-control", "type": "date", "required": True}
            ),
            "quotation_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Quotation Number",
                    "required": True,
                    "maxlength": 11,
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Email",
                }
            ),
            "address": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Address",
                    "required": True,
                }
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
                    "required": True,
                }
            ),
            "letterhead": forms.CheckboxInput(
                attrs={"class": "form-check-input", "required": True}
            ),
            "due_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date", "required": True}
            ),
        }


class QuotationGeneralForm(forms.ModelForm):
    class Meta:
        model = QuotationGeneral
        fields = [
            "client_name",
            "company_name",
            "phone",
            "email",
            "address",
            "subject",
            "notes",
            "letterhead",
            "due_date",
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
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Email",
                }
            ),
            "address": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Address",
                    "required": True,
                }
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
                    "required": True,
                }
            ),
            "letterhead": forms.CheckboxInput(
                attrs={"class": "form-check-input", "required": False}
            ),
            "due_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date", "required": True}
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
                Column("email", css_class="form-group col-md-12 mb-3"), css_class="row"
            ),
            Row(
                Column("subject", css_class="form-group col-md-6 mb-3"),
                Column("notes", css_class="form-group col-md-6 mb-3"),
                css_class="row",
            ),
            Row(
                Column("due_date", css_class="form-group col-md-6 mb-3"),
                Column("letterhead", css_class="form-check mt-4 ms-2"),
                css_class="row",
            ),
        )


class ItemGeneralForm(forms.ModelForm):
    class Meta:
        model = ItemGeneral
        fields = ["item_name", "description", "quantity", "rate", "tax"]

        widgets = {
            "item_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Item Name",
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
                    "placeholder": "Quantity",
                    "required": True,
                }
            ),
            "rate": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Rate", "required": True}
            ),
            "tax": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Tax (%)",
                    "required": False,
                    "maxlength": 3,
                    "step": "0.1",
                }
            ),
        }

from django import forms
from .models import Quotation
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column


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
                attrs={"class": "form-control", "placeholder": "Client Name"}
            ),
            "company_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Company Name"}
            ),
            "phone": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Phone Number"}
            ),
            "email": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "Email"}
            ),
            "address": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Address"}
            ),
            "subject": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Subject"}
            ),
            "notes": forms.Textarea(
                attrs={"class": "form-control", "placeholder": "Notes"}
            ),
            "letterhead": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "due_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
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


from django import forms
from .models import QuotationItem


class QuotationItemForm(forms.ModelForm):
    class Meta:
        model = QuotationItem
        fields = ["item_name", "description", "quantity", "rate", "tax"]

        widgets = {
            "item_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Item Name"}
            ),
            "description": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Description"}
            ),
            "quantity": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Quantity"}
            ),
            "rate": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Rate"}
            ),
            "tax": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Tax (%)"}
            ),
        }

    def clean(self):
        cleaned_data = super().clean()
        # Optionally, add custom validation if required
        return cleaned_data

    def save(self, *args, **kwargs):
        instance = super().save(commit=False)
        # Calculate amount including tax
        instance.save()  # Automatically updates the amount and total
        return instance

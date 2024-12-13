from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML
from crispy_forms.layout import Layout, Row, Column, Submit
from django import forms
from phonenumber_field.formfields import PhoneNumberField

from .models import Customer


class CustomerForm(forms.ModelForm):
    mobile = PhoneNumberField(
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Mobile"}
        ),
        error_messages={"invalid": "Enter a valid mobile phone number."},
    )
    phone = PhoneNumberField(
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Phone"}),
        error_messages={"invalid": "Enter a valid phone number."},
        required=False,
    )

    class Meta:
        model = Customer
        fields = [
            "salutation",
            "first_name",
            "last_name",
            "company_name",
            "customer_type",
            "email",
            "mobile",
            "phone",
            "currency",
            "payment_due_period",
            "company_id",
        ]

        labels = {
            "customer_type": "Customer Type:",
            "company_name": "Company Name:",
            "email": "Email:",
            "phone": "Phone:",
        }

        widgets = {
            "salutation": forms.Select(attrs={"class": "form-select"}),
            "payment_due_period": forms.Select(attrs={"class": "form-select"}),
            "first_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "First Name"}
            ),
            "last_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Last Name"}
            ),
            "company_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Company Name"}
            ),
            "customer_type": forms.Select(attrs={"class": "form-select"}),
            "email": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "Email"}
            ),
            "company_id": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Company ID"}
            ),
            "other_details": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Other Details",
                }
            ),
            "currency": forms.Select(attrs={"class": "form-select"}),
        }

    def clean_mobile(self):
        mobile = self.cleaned_data.get("mobile")
        if not str(mobile).startswith(("+92", "03")):
            raise forms.ValidationError(
                "Mobile number must start with +92 or 03 (for Pakistan)."
            )
        return mobile

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if str(phone) == "":
            return None
        elif not str(phone).startswith(("+92", "03")):
            raise forms.ValidationError(
                "Phone number must start with +92 or 03 (for Pakistan)."
            )
        return phone

    def clean(self):
        cleaned_data = super().clean()
        fields_to_validate = [
            "first_name",
            "last_name",
            "company_name",
        ]

        for field in fields_to_validate:
            value = cleaned_data.get(field)
            if value and not value.isalnum():
                self.add_error(
                    field,
                    f"{field.replace('_', ' ').capitalize()} should only contain alphanumeric characters.",
                )

        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_class = "row g-3"  # Bootstrap spacing for form rows
        self.helper.layout = Layout(
            Row(
                Column("customer_type", css_class="form-group mb-3"),
            ),
            Row(Column("company_name", css_class="col-md-12 mb-3"), css_class="row"),
            Row(HTML('<h4 class="m-2 ms-0">Primary Contact</h4>'), css_class="col-12"),
            Row(
                Column("salutation", css_class="form-group col-md-4 mb-3"),
                Column("first_name", css_class="form-group col-md-4 mb-3"),
                Column("last_name", css_class="form-group col-md-4 mb-3"),
                css_class="row",
            ),
            Row(
                Column("email", css_class="form-group col-md-12 mb-3"), css_class="row"
            ),
            Row(
                Column("mobile", css_class="form-group col-md-6 mb-3"),
                Column("phone", css_class="form-group col-md-6 mb-3"),
                css_class="row",
            ),
            Row(
                Column("currency", css_class="form-group col-md-6 mb-3"),
                Column("company_id", css_class="form-group col-md-6 mb-3"),
                css_class="row",
            ),
            Row(
                Column("payment_due_period", css_class="form-group col-md-12 mb-3"),
                css_class="row",
            ),
            FormActions(Submit("submit", "Submit", css_class="btn btn-primary")),
        )

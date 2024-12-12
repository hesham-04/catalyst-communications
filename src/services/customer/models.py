from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class Customer(models.Model):
    CUSTOMER_TYPE_CHOICES = [
        ("business", "Business"),
        ("individual", "Individual"),
    ]
    CURRENCY_CHOICES = [
        ("USD", "US Dollar"),
        ("EUR", "Euro"),
        ("PKR", "Pakistani Rupee"),
    ]
    PAYMENT_DUE_CHOICES = [
        ("net_15", "Net 15"),
        ("net_45", "Net 45"),
        ("net_60", "Net 60"),
        ("due_receipt", "Due On Receipt"),
        ("due_eom", "Due End of Month"),
    ]
    salutation = models.CharField(
        max_length=10,
        choices=[("Mr.", "Mr."), ("Ms.", "Ms."), ("Mrs.", "Mrs.")],
        default="Mr.",
    )
    first_name = models.CharField(max_length=18)
    last_name = models.CharField(max_length=18, blank=True)
    company_name = models.CharField(max_length=20, blank=True)
    customer_type = models.CharField(
        max_length=10, choices=CUSTOMER_TYPE_CHOICES, default="business"
    )
    email = models.EmailField()
    phone = PhoneNumberField(blank=True, null=True, max_length=15)
    mobile = PhoneNumberField(
        max_length=15,
    )
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default="PKR")
    payment_due_period = models.CharField(
        max_length=15, choices=PAYMENT_DUE_CHOICES, default="due_eom"
    )
    company_id = models.CharField(max_length=50, unique=True, blank=True, null=True)

    def get_full_name(self):
        return f"{self.salutation} {self.first_name} {self.last_name}"

    def __str__(self):
        return f"{self.salutation} {self.first_name} {self.last_name}"

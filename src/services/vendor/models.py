from django.db import models
from django.db.models import Sum
from phonenumber_field.modelfields import PhoneNumberField

from src.services.expense.models import Expense


class Vendor(models.Model):
    CURRENCY_CHOICES = [
        ("USD", "US Dollar"),
        ("EUR", "Euro"),
        ("PKR", "Pakistani Rupee"),
    ]

    name = models.CharField(max_length=255, unique=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    iban = models.CharField(max_length=34, blank=True, null=True)

    email = models.EmailField(max_length=255, blank=True, null=True)
    phone = PhoneNumberField(blank=True, null=True, region="PK")

    registration_number = models.CharField(max_length=50, blank=True, null=True)
    vat_number = models.CharField(max_length=50, blank=True, null=True)
    website = models.URLField(blank=True, null=True)

    # total_expense = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default="USD")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def total_expense(self):
        return (
            self.expenses.filter(payment_status=Expense.PaymentStatus.PAID).aggregate(
                total=Sum("amount")
            )["total"]
            or 0
        )

    def get_unpaid_expenses(self):
        """
        Returns a queryset of all unpaid expenses related to this vendor.
        """
        return self.expenses.filter(payment_status=Expense.PaymentStatus.UNPAID)

    def get_total_unpaid_expenses(self):
        """
        Returns the total amount of all unpaid expenses for this vendor.
        """
        unpaid_expenses = self.get_unpaid_expenses()
        total = unpaid_expenses.aggregate(total=Sum("amount"))["total"] or 0
        return round(total, 2)

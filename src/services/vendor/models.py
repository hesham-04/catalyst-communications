from django.db import models
from django.db.models import Sum

from src.services.expense.models import Expense


class Vendor(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255, blank=True, null=True)
    iban = models.CharField(max_length=34, blank=True, null=True)  # Bank account IBAN

    email = models.EmailField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)

    registration_number = models.CharField(max_length=50, blank=True, null=True)  # Company registration number
    vat_number = models.CharField(max_length=50, blank=True, null=True)  # VAT identification number
    website = models.URLField(blank=True, null=True)

    total_expense = models.DecimalField(max_digits=12, decimal_places=2, default=0)  # Total expenses paid to the vendor
    currency = models.CharField(max_length=10, default='USD')  # Default transaction currency

    is_active = models.BooleanField(default=True)  # Whether the vendor is active
    created_at = models.DateTimeField(auto_now_add=True)  # Record creation date
    updated_at = models.DateTimeField(auto_now=True)  # Last update timestamp

    def __str__(self):
        return self.name

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
        total = unpaid_expenses.aggregate(total=Sum('amount'))['total'] or 0
        return round(total, 2)

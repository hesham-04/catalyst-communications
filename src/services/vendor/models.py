from django.db import models
from django.db.models import Sum
from phonenumber_field.modelfields import PhoneNumberField

from src.services.expense.models import Expense
from src.services.transaction.models import Ledger
from src.web.dashboard.utils import ledger_filter
from django.db import models
from django.db.models import Sum, Q



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

    from django.db.models import Sum

    @property
    def total_expense(self):
        """
        Computes the total paid expenses for the vendor based on related ledger transactions.
        Returns:
            Decimal: Total sum of paid expenses. Returns 0 if no transactions exist.
        """
        total = ledger_filter(destination=self).aggregate(total=Sum("amount"))["total"]
        return total if total is not None else 0

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


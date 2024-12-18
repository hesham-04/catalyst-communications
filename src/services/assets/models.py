from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum

from src.services.expense.models import ExpenseCategory


# Create your models here.


class CashInHand(models.Model):
    name = models.CharField(max_length=255, unique=True)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateField(auto_now_add=True, null=True)

    def adjust_balance(self, amount, transaction_type):
        """
        Adjusts the account balance based on the transaction type. THIS CREDIT DOES NOT REFER TO AMOUNT BEING CREDITED
        INTO ACCOUNT BALANCE, RATHER AMOUNT BEING CREDITED TO A PROJECT BUDGET
        :param amount:
        :param transaction_type:
        :return:
        """
        if transaction_type == "CREDIT":
            if self.balance < amount:
                raise ValueError("Insufficient cash in hand")
            else:
                self.balance -= amount
        elif transaction_type == "DEBIT":
            self.balance += amount
        self.save()

    def save(self, *args, **kwargs):
        if not self.pk and CashInHand.objects.exists():
            return False
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Cash in Hand Balance: {self.balance}"


class AccountBalance(models.Model):
    account_name = models.CharField(max_length=255, unique=True)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    starting_balance = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00, null=True, blank=True
    )
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateField(auto_now_add=True, null=True)

    def adjust_balance(self, amount, transaction_type):
        """
        Adjusts the account balance based on the transaction type. THIS CREDIT DOES NOT REFER TO AMOUNT BEING CREDITED
        INTO ACCOUNT BALANCE, RATHER AMOUNT BEING CREDITED TO A PROJECT BUDGET
        :param amount:
        :param transaction_type:
        :return:
        """
        if transaction_type == "CREDIT":
            if self.balance < amount:
                raise ValueError("Insufficient funds in account")
            else:
                self.balance -= amount
        elif transaction_type == "DEBIT":
            self.balance += amount
        self.save()

    @classmethod
    def get_total_balance(cls):
        """
        Calculates the sum of all account balances.
        :return: Decimal - Total balance across all accounts
        """
        from django.db.models import Sum

        total_balance = cls.objects.aggregate(total=Sum("balance"))["total"]
        return total_balance or 0

    def __str__(self):
        return f"{self.account_name} - Balance: {self.balance} PKR"

    @classmethod
    def deduct_from_balance(cls, amount):
        accounts = cls.objects.filter(balance__gt=0).order_by("-balance")
        for account in accounts:
            if amount <= 0:
                break
            if account.balance >= amount:
                account.balance -= amount
                account.save()
                amount = 0
            else:
                amount -= account.balance
                account.balance = 0
                account.save()
        if amount > 0:
            raise ValidationError("Insufficient account balance.")

    def save(self, *args, **kwargs):
        if not self.pk:
            self.starting_balance = self.balance
            super().save(*args, **kwargs)
        super().save(*args, **kwargs)

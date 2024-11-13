from django.db import models

# Create your models here.

class CashInHand(models.Model):
    name = models.CharField(max_length=255, unique=True)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    updated_at = models.DateTimeField(auto_now=True)

    def adjust_balance(self, amount, transaction_type):
        """
            Adjusts the account balance based on the transaction type. THIS CREDIT DOES NOT REFER TO AMOUNT BEING CREDITED
            INTO ACCOUNT BALANCE, RATHER AMOUNT BEING CREDITED TO A PROJECT BUDGET
            :param amount:
            :param transaction_type:
            :return:
        """
        if transaction_type == 'CREDIT':
            if self.balance < amount:
                raise ValueError("Insufficient cash in hand")
            else:
                self.balance -= amount
        elif transaction_type == 'DEBIT':
            self.balance += amount
        self.save()

    def __str__(self):
        return f"Cash in Hand Balance: {self.balance}"




class AccountBalance(models.Model):
    account_name = models.CharField(max_length=255, unique=True)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    updated_at = models.DateTimeField(auto_now=True)

    def adjust_balance(self, amount, transaction_type):
        """
        Adjusts the account balance based on the transaction type. THIS CREDIT DOES NOT REFER TO AMOUNT BEING CREDITED
        INTO ACCOUNT BALANCE, RATHER AMOUNT BEING CREDITED TO A PROJECT BUDGET
        :param amount:
        :param transaction_type:
        :return:
        """
        if transaction_type == 'CREDIT':
            if self.balance < amount:
                raise ValueError("Insufficient funds in account")
            else:
                self.balance -= amount
        elif transaction_type == 'DEBIT':
            self.balance += amount
        self.save()

    def __str__(self):
        return f"{self.account_name} - Balance: {self.balance}"
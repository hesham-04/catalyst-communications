from django.db import models
from src.services.customer.models import Customer


class BillingAddress(models.Model):
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, related_name='billing_address')
    attention = models.CharField(max_length=100, blank=True)
    country_region = models.CharField(max_length=100)
    street_1 = models.CharField(max_length=100)
    street_2 = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=10)
    phone = models.CharField(max_length=15, blank=True)
    fax = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return f"{self.customer.display_name} - Billing - {self.city}, {self.state}"


class ShippingAddress(models.Model):
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, related_name='shipping_address')
    attention = models.CharField(max_length=100, blank=True)
    country_region = models.CharField(max_length=100)
    street_1 = models.CharField(max_length=100)
    street_2 = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=10)
    phone = models.CharField(max_length=15, blank=True)
    fax = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return f"{self.customer.display_name} - Shipping - {self.city}, {self.state}"



class Tax(models.Model):
    name = models.CharField(max_length=50)
    rate = models.DecimalField(max_digits=5, decimal_places=2)
    is_compound = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Transaction(models.Model):
    class TransactionType(models.TextChoices):
        DEBIT = 'DEBIT', 'Debit'
        CREDIT = 'CREDIT', 'Credit'

    project = models.ForeignKey('project.Project', on_delete=models.CASCADE, related_name='transactions')
    source = models.CharField(max_length=6, choices=[('BANK', 'Bank'), ('CASH', 'Cash in Hand'), ('ACC', 'Account'), ('CLIENT', 'Client Provided')])
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_type = models.CharField(max_length=6, choices=TransactionType.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.project} - {self.transaction_type} {self.amount} from {self.source}"

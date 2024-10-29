from django.db import models
from src.services.customer.models import Customer


class Address(models.Model):
    ADDRESS_TYPE_CHOICES = [
        ('billing', 'Billing Address'),
        ('shipping', 'Shipping Address'),
    ]

    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, related_name='address')
    address_type = models.CharField(max_length=10, choices=ADDRESS_TYPE_CHOICES)
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
        return f"{self.customer.display_name} - {self.address_type.capitalize()} - {self.city}, {self.state}"
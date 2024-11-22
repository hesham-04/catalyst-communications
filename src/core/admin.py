from django.contrib import admin
from .models import ShippingAddress, BillingAddress, Tax

# Register your models here

admin.site.register(ShippingAddress)
admin.site.register(BillingAddress)
admin.site.register(Tax)

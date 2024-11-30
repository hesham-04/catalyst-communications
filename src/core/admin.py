from django.contrib import admin
from .models import BillingAddress, Tax

# Register your models here

admin.site.register(BillingAddress)
admin.site.register(Tax)

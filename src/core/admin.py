from django.contrib import admin
from .models import ShippingAddress, BillingAddress, CashInHand, Tax, AccountBalance, Transaction

# Register your models here

admin.site.register(ShippingAddress)
admin.site.register(BillingAddress)
admin.site.register(CashInHand)
admin.site.register(Tax)
admin.site.register(AccountBalance)
admin.site.register(Transaction)

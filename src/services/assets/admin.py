from django.contrib import admin
from .models import CashInHand, AccountBalance

# Register your models here.
admin.site.register(CashInHand)
admin.site.register(AccountBalance)

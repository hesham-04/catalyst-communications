from django.contrib import admin
from .models import Expense, Vendor, ExpenseCategory
# Register your models here.

admin.site.register(Expense)
admin.site.register(Vendor)
admin.site.register(ExpenseCategory)

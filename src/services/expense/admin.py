from django.contrib import admin
from .models import Expense, ExpenseCategory, JournalExpense

# Register your models here.

admin.site.register(Expense)
admin.site.register(ExpenseCategory)
admin.site.register(JournalExpense)
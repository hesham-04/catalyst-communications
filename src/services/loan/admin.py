from django.contrib import admin
from .models import Lender, Loan, LoanReturn
# Register your models here.
admin.site.register(Lender)
admin.site.register(Loan)
admin.site.register(LoanReturn)
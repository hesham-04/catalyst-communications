from django.contrib import admin
from .models import Invoice, InvoiceItem

# Register your models here.
admin.site.register(InvoiceItem)
admin.site.register(Invoice)
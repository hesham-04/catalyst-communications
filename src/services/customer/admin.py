from django.contrib import admin
from .models import Customer, ContactPerson

# Register your models here.
admin.site.register(Customer)
admin.site.register(ContactPerson)
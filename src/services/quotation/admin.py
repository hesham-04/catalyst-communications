from django.contrib import admin
from .models import Quotation, QuotationItem

# Define the inline admin class for QuotationItem
class QuotationItemInline(admin.TabularInline):  # Use TabularInline or StackedInline based on preference
    model = QuotationItem
    extra = 1  # Number of empty forms displayed for new items
    fields = ['item_name', 'description', 'quantity', 'rate', 'amount']  # Customize fields shown
    readonly_fields = ['amount']  # Make 'amount' read-only since it auto-calculates

# Customize the Quotation admin to include QuotationItem inline
class QuotationAdmin(admin.ModelAdmin):
    inlines = [QuotationItemInline]
    list_display = ['quotation_number', 'client_name', 'project', 'total_amount']  # Fields to show in list view
    search_fields = ['quotation_number', 'client_name', 'project__project_name']  # Search fields

# Register the models with the customized admin
admin.site.register(Quotation, QuotationAdmin)

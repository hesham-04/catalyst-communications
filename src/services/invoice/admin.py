from django.contrib import admin
from .models import Invoice, InvoiceItem


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1  # Number of empty forms displayed by default
    fields = ("item_name", "description", "quantity", "rate", "tax", "amount")
    readonly_fields = ("amount",)  # Prevent manual edits to calculated fields

    def get_queryset(self, request):
        # Customize queryset if needed, such as filtering by related project or status
        return super().get_queryset(request)


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        "invoice_number",
        "client_name",
        "project",
        "total_amount",
        "status",
        "due_date",
        "created_at",
    )
    list_filter = ("status", "created_at", "due_date")
    search_fields = ("invoice_number", "client_name", "project__project_name")
    date_hierarchy = "created_at"

    readonly_fields = ("total_amount", "total_in_words", "invoice_number")
    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "invoice_number",
                    "date",
                    "client_name",
                    "company_name",
                    "phone",
                    "address",
                    "email",
                    "project",
                )
            },
        ),
        (
            "Details",
            {
                "fields": (
                    "subject",
                    "notes",
                    "total_amount",
                    "total_in_words",
                    "status",
                    "due_date",
                    "letterhead",
                    "tax",
                )
            },
        ),
    )
    inlines = [InvoiceItemInline]

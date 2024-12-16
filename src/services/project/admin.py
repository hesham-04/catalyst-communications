from django.contrib import admin
from django.db.models import Sum

from .models import Project


from django.contrib import admin

from ..invoice.models import Invoice
from ..quotation.models import Quotation


class InvoiceInline(
    admin.TabularInline
):  # Or admin.StackedInline for a stacked display
    model = Invoice
    extra = 0  # Number of empty forms to display
    fields = (
        "invoice_number",
        "date",
        "client_name",
        "total_amount",
        "status",
        "due_date",
    )
    readonly_fields = ("invoice_number", "total_amount", "status", "due_date")


class QuotationInline(admin.TabularInline):  # If you have a Quotation model
    model = Quotation
    extra = 0
    fields = (
        "quotation_number",
        "total_amount",
    )  # Modify as per your Quotation model fields
    readonly_fields = ("quotation_number", "total_amount")


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        "project_name",
        "customer",
        "project_status",
        "budget_source",
        "project_cash",
        "project_account_balance",
        "get_total_budget",
        "created_at",
    )
    list_filter = ("project_status", "budget_source", "created_at")
    search_fields = ("project_name", "customer__name")
    readonly_fields = (
        "get_total_budget",
        "get_trial_balance",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Project Details",
            {
                "fields": (
                    "project_name",
                    "description",
                    "customer",
                    "project_status",
                    "budget_source",
                )
            },
        ),
        (
            "Budget Information",
            {"fields": ("project_cash", "project_account_balance", "get_total_budget")},
        ),
        ("Trial Balance", {"fields": ("get_trial_balance",)}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )

    def get_total_budget(self, obj):
        return obj.get_total_budget()

    get_total_budget.short_description = "Total Budget"

    def get_trial_balance(self, obj):
        balance = obj.get_trial_balance()
        return (
            f"Total Invoices (Credit): {balance['Total Invoices (Credit)']}, "
            f"Total Expenses (Debit): {balance['Total Expenses (Debit)']}, "
            f"Net Balance: {balance['Net Balance']}"
        )

    get_trial_balance.short_description = "Trial Balance"

    actions = ["export_trial_balance"]

    def export_trial_balance(self, request, queryset):
        # Implement logic to export trial balance to a file or display a report
        self.message_user(
            request, f"Exported trial balances for {queryset.count()} projects."
        )

    export_trial_balance.short_description = "Export Trial Balance"

    # Add inlines for Invoice and Quotation
    inlines = [InvoiceInline, QuotationInline]

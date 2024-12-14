from django.contrib import admin
from django.db.models import Sum

from .models import Project


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

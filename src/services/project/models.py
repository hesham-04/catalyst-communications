from django.db import models
from django.db.models import Sum

from src.core.models import BillingAddress


class Project(models.Model):
    class ProjectStatus(models.TextChoices):
        DRAFT = "DF", "Draft"
        AWAITING = "AW", "Awaiting Quote Approval"
        CANCELLED = "CL", "Cancelled"
        IN_PROGRESS = "IP", "In Progress"
        FINISHED = "FN", "Finished"

    class BudgetSource(models.TextChoices):
        CASH = "CASH", "Cash in Hand"
        ACCOUNT = "ACC", "Account"

    project_name = models.CharField(
        max_length=255, help_text="Name of the project", blank=True
    )
    description = models.TextField(
        help_text="Description of the project", blank=True, null=True
    )
    customer = models.ForeignKey(
        "customer.Customer", on_delete=models.CASCADE, related_name="projects"
    )

    # Project Assets
    project_cash = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        help_text="Cash in hand assigned to the project",
    )
    project_account_balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        help_text="Account funds assigned to the project",
    )

    project_status = models.CharField(
        max_length=2,
        choices=ProjectStatus.choices,
        default=ProjectStatus.DRAFT,
        help_text="Current status of the project",
    )

    budget_source = models.CharField(
        max_length=6,
        choices=BudgetSource.choices,
        default=BudgetSource.CASH,
        help_text="Source of the project budget",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.project_name or 'Project'}"

    def get_total_budget(self):
        return self.project_cash + self.project_account_balance

    def get_address(self):
        billing_address = BillingAddress.objects.filter(
            customer_id=self.customer.pk
        ).first()
        if billing_address:
            return f"{billing_address.city} - {billing_address.state}"
        else:
            return f"Customer Address Not Defined"

    def get_trial_balance(self):
        total_invoices = (
            self.invoices.aggregate(total=Sum("total_amount"))["total"] or 0
        )
        total_expenses = self.expenses.aggregate(total=Sum("amount"))["total"] or 0
        cash_balance = self.project_cash
        account_balance = self.project_account_balance

        return {
            "Total Invoices (Credit)": total_invoices,
            "Total Expenses (Debit)": total_expenses,
            "Cash Balance": cash_balance,
            "Account Balance": account_balance,
            "Net Balance": (
                cash_balance + account_balance + total_invoices - total_expenses
            ),
        }

    def generate_trial_balance(self):
        trial_balance = []
        invoices_total = (
            self.invoices.aggregate(total=Sum("total_amount"))["total"] or 0
        )
        expenses_total = self.expenses.aggregate(total=Sum("amount"))["total"] or 0

        trial_balance.append({"Account": "Invoices (Credit)", "Amount": invoices_total})
        trial_balance.append({"Account": "Expenses (Debit)", "Amount": expenses_total})
        trial_balance.append(
            {"Account": "Net Balance", "Amount": invoices_total - expenses_total}
        )
        return trial_balance

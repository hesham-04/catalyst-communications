from django.db import models
from src.services.project.models import Project


class Ledger(models.Model):

    TRANSACTION_TYPES = [
        ("BUDGET_ASSIGN", "Budget Assigned to Project"),  # From Main ACC to Project
        ("TRANSFER", "Funds Transfer"),  # Only from Project ACC to Project CASH
        ("CREATE_LOAN", "Loan Created"),  # Project Loan
        ("RETURN_LOAN", "Loan Returned"),  # Return
        ("MISC_LOAN_CREATE", "Miscellaneous Loan"),
        ("MISC_LOAN_RETURN", "Miscellaneous Loan Return"),
        ("CREATE_EXPENSE", "Expense Created"),
        ("MISC_EXPENSE", " Miscellaneous Expense Created"),
        ("ADD_CASH", "Added Cash"),  # Cash Added to The General Cash in Hand
        ("INVOICE_PAYMENT", "Invoice Paid"),
        ("ADD_ACC_BALANCE", "Balance Added"),
    ]

    transaction_type = models.CharField(max_length=50, choices=TRANSACTION_TYPES)
    project = models.ForeignKey(
        Project, on_delete=models.SET_NULL, null=True, blank=True
    )
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    source = models.CharField(max_length=255, blank=True, null=True)
    destination = models.CharField(max_length=255, blank=True, null=True)
    category = models.CharField(max_length=255, blank=True, null=True)
    reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Project: {self.project} - Source: {self.source} - Destination: {self.destination} - {self.transaction_type}: {self.amount}"

    class Meta:
        ordering = ["-created_at"]

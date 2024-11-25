from django.db import models
from src.services.project.models import Project


class Ledger(models.Model):
    TRANSACTION_TYPES = [
        ('BUDGET_ASSIGN', 'Budget Assigned to Project'),
        ('TRANSFER', 'Funds Transfer'),

        ('CREATE_LOAN', 'Loan Created'),
        ('RETURN_LOAN', 'Loan Returned'),

        ('CREATE_EXPENSE', 'Expense Created'),
        ('PAY_EXPENSE', 'Expense Paid'),

        ('INVOICE_PAYMENT', 'Invoice Paid')
    ]

    transaction_type = models.CharField(max_length=50, choices=TRANSACTION_TYPES)
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    source = models.CharField(max_length=255, blank=True, null=True)
    destination = models.CharField(max_length=255, blank=True, null=True)
    reason= models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Project: {self.project} - Source: {self.source} - Destination: {self.destination} - {self.transaction_type}: {self.amount}"


    class Meta:
        ordering = ['-created_at']
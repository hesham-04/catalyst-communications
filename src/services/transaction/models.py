from django.contrib import messages
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.shortcuts import redirect

from src.services.project.models import Project
from src.services.transaction.repercussions import delete_transaction_instance


class Ledger(models.Model):

    TRANSACTION_TYPES = [
        (
            "BUDGET_ASSIGN",
            "Budget Assigned to Project",  # From Main ACC to Project ( CAN ONLY BE TRANSFERRED FORM ACC TO PROJ CASH )
        ),
        ("TRANSFER", "Funds Transfer"),  # Only from Project ACC to Project CASH
        ("CREATE_LOAN", "Loan Created"),  # Project Loan Created
        ("RETURN_LOAN", "Loan Returned"),  # Project Loan Return
        ("MISC_LOAN_CREATE", "Miscellaneous Loan"),  # MISCELLANEOUS LOAN CREATED
        ("MISC_LOAN_RETURN", "Miscellaneous Loan Return"),  # MISCELLANEOUS LOAN RETURN
        ("CREATE_EXPENSE", "Expense Created"),  # PROJ EXPENSE CREATED
        (
            "MISC_EXPENSE",
            " Miscellaneous Expense Created",  # MISCELLANEOUS EXPENSE CREATED
        ),
        ("ADD_CASH", "Added Cash"),  # Add Cash to Petty Cash General.
        ("INVOICE_PAYMENT", "Invoice Paid"),  # Project Invoice Payment
        (
            "ADD_ACC_BALANCE",
            "Balance Added",  # Update General Account Balance [ NOT IMPLEMENTED ] TODO: IMPLEMENT THIS
        ),
    ]

    transaction_type = models.CharField(max_length=50, choices=TRANSACTION_TYPES)
    project = models.ForeignKey(
        Project, on_delete=models.SET_NULL, null=True, blank=True
    )
    amount = models.DecimalField(max_digits=15, decimal_places=2)

    # Source fields (Generic Relation)
    source_content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, related_name="source_ledgers"
    )
    source_object_id = models.PositiveIntegerField()
    source = GenericForeignKey("source_content_type", "source_object_id")

    # Destination fields (Generic Relation)
    destination_content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, related_name="destination_ledgers"
    )
    destination_object_id = models.PositiveIntegerField()
    destination = GenericForeignKey("destination_content_type", "destination_object_id")

    expense_category = models.ForeignKey(
        "expense.ExpenseCategory", on_delete=models.SET_NULL, null=True, blank=True
    )
    reason = models.TextField(blank=True, null=True)

    # DELETE FIELDS:
    misc_expense = models.ForeignKey(
        "expense.JournalExpense",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="This is populated only when creating misc expense instance",
    )
    expense = models.ForeignKey(
        "expense.Expense",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="This is populated only when creating a return loan & expense create instance",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_type} {self.amount} from {self.source} to {self.destination}"

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["project"]),
            models.Index(fields=["transaction_type"]),
        ]

    def delete(self, *args, **kwargs):
        # Perform any pre-delete actions here
        # If Source or Destination is Project then the subtraction or addition is possible from two fields:
        # [ (project_account_balance), (project_cash) ]
        try:
            delete_transaction_instance(
                transaction_type=self.transaction_type,
                source=self.source,
                destination=self.destination,
                amount=self.amount,
                ledger=self.pk,
            )
        except Exception as e:
            messages.error(self.request, f"An error occurred: {e}")
            return redirect("transaction:list")
        super().delete(*args, **kwargs)

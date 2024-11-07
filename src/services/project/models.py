from django.db import models
from django.utils import timezone

from src.core.models import Transaction, CashInHand, AccountBalance


class Project(models.Model):
    class ProjectStatus(models.TextChoices):
        DRAFT = 'DF', 'Draft'
        QUOTATION = 'QT', 'Quotation'
        AWAITING = 'AW', 'Awaiting Approval'
        CANCELLED = 'CL', 'Cancelled'
        IN_PROGRESS = 'IP', 'In Progress'
        FINISHED = 'FN', 'Finished'

    class BudgetSource(models.TextChoices):
        BANK = 'BANK', 'Bank'
        CASH = 'CASH', 'Cash in Hand'
        ACCOUNT = 'ACC', 'Account'
        CLIENT_FUNDS = 'CLIENT', 'Client Provided'

    project_name = models.CharField(max_length=255, help_text="Name of the project", blank=True)
    description = models.TextField(help_text="Description of the project", blank=True, null=True)
    customer = models.ForeignKey('customer.Customer', on_delete=models.CASCADE, related_name='projects')

    # Specific budget fields for different sources
    project_budget = models.DecimalField(max_digits=12, decimal_places=2, default=0.00,
                                         help_text="Total project budget")
    project_cash = models.DecimalField(max_digits=12, decimal_places=2, default=0.00,
                                       help_text="Cash in hand assigned to the project")
    project_account_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00,
                                                  help_text="Account funds assigned to the project")
    project_client_fund = models.DecimalField(max_digits=12, decimal_places=2, default=0.00,
                                              help_text="Client funds assigned to the project")

    client_funds_received = models.DecimalField(max_digits=12, decimal_places=2, default=0.00,
                                                help_text="Total funds provided by the client")
    project_loan_recieved = models.DecimalField(max_digits=12, decimal_places=2, default=0.00,
                                                help_text="Total loan amount received by the project")
    project_status = models.CharField(
        max_length=2,
        choices=ProjectStatus.choices,
        default=ProjectStatus.DRAFT,
        help_text="Current status of the project"
    )

    budget_source = models.CharField(
        max_length=6,
        choices=BudgetSource.choices,
        default=BudgetSource.CASH,
        help_text="Source of the project budget"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.project_name or 'Project'} - {self.get_project_status_display()}"

    def adjust_budget(self, amount, source, transaction_type):
        """
        Adjusts the budget based on the source and transaction type.
        :param amount: The amount to add/subtract
        :param source: The source of the funds (e.g., BANK, CASH, ACC, CLIENT)
        :param transaction_type: 'CREDIT' for adding funds, 'DEBIT' for deducting funds
        """
        # Create transaction record
        Transaction.objects.create(
            project=self,
            source=source,
            amount=amount,
            transaction_type=transaction_type
        )

        # Adjust specific fields based on the source
        if source == 'CASH':
            cash = CashInHand.objects.first()
            cash.adjust_balance(amount, transaction_type)
            if transaction_type == 'CREDIT':
                self.project_cash += amount
            else:
                self.project_cash -= amount

        elif source == 'ACC':
            account = AccountBalance.objects.first()
            account.adjust_balance(amount, transaction_type)
            if transaction_type == 'CREDIT':
                self.project_account_balance += amount
            else:
                self.project_account_balance -= amount

        elif source == 'CLIENT':
            if transaction_type == 'CREDIT':
                self.client_funds_received += amount
                self.project_client_fund += amount
            else:
                self.project_client_fund -= amount

        elif source == 'LOAN':
            print("source loan ----------")
            if transaction_type == 'CREDIT':
                print('source loan credit ----------')
                print("amount", amount)
                print("self.project_budget before", self.project_budget)
                self.project_budget += amount
                print("self.project_budget after", self.project_budget)
                self.project_loan_recieved += amount
            else:
                self.project_budget -= amount

        self.save()


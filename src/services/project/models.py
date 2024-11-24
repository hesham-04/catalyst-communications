from django.db import models

from src.core.models import BillingAddress, ShippingAddress
from src.services.assets.models import CashInHand, AccountBalance


class Project(models.Model):
    class ProjectStatus(models.TextChoices):
        DRAFT = 'DF', 'Draft'
        AWAITING = 'AW', 'Awaiting Quote Approval'
        CANCELLED = 'CL', 'Cancelled'
        IN_PROGRESS = 'IP', 'In Progress'
        FINISHED = 'FN', 'Finished'

    class BudgetSource(models.TextChoices):
        CASH = 'CASH', 'Cash in Hand'
        ACCOUNT = 'ACC', 'Account'

    project_name = models.CharField(max_length=255, help_text="Name of the project", blank=True)
    description = models.TextField(help_text="Description of the project", blank=True, null=True)
    customer = models.ForeignKey('customer.Customer', on_delete=models.CASCADE, related_name='projects')

    # Project Assets
    project_cash = models.DecimalField(max_digits=12, decimal_places=2, default=0.00,
                                       help_text="Cash in hand assigned to the project")
    project_account_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00,
                                                  help_text="Account funds assigned to the project")

    total_budget_assigned = models.DecimalField(max_digits=12, decimal_places=2, default=0.00,
                                                help_text="Total cumulative budget assigned to the project")

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
        return f"{self.project_name or 'Project'}"

    def get_total_budget(self):
        return self.project_cash + self.project_account_balance


    def get_address(self):
        billing_address = BillingAddress.objects.filter(customer_id=self.customer.pk).first()
        shipping_address = ShippingAddress.objects.filter(customer_id=self.customer.pk).first()
        if billing_address:
            return f"{billing_address.city} - {billing_address.state}"
        elif shipping_address:
            return f"{shipping_address.city} - {shipping_address.state}"
        else:
            return None

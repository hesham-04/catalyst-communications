from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Sum


class ExpenseCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Vendor(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    iban = models.CharField(max_length=34)

    def __str__(self):
        return self.name

    @classmethod
    def most_used_vendor(cls):
        most_used_vendor = (
            cls.objects.values('vendor')
            .annotate(total_expense=Sum('amount'))
            .order_by('-total_expense')
            .first()
        )

        if most_used_vendor and most_used_vendor['vendor']:
            vendor = Vendor.objects.get(id=most_used_vendor['vendor'])
            return vendor, round(most_used_vendor['total_expense'], 2)

        return None, 0



class Expense(models.Model):

    class BudgetSource(models.TextChoices):
        CASH = 'CASH', 'Cash in Hand'
        ACCOUNT = 'ACC', 'Account'
        CLIENT_FUNDS = 'CLIENT', 'Client Provided'
        LOAN = 'LOAN', 'Project Loan'

    project = models.ForeignKey('project.Project', on_delete=models.CASCADE, related_name='expenses')
    description = models.CharField(max_length=255, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    budget_source = models.CharField(max_length=6, choices=BudgetSource.choices, null=True, blank=True)
    category = models.ForeignKey(ExpenseCategory, on_delete=models.SET_NULL, null=True, blank=True,  related_name='expenses')
    vendor = models.ForeignKey('Vendor', on_delete=models.SET_NULL, null=True, related_name='expenses')  # Link to Vendor model
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.project.project_name} - {self.amount} from {self.budget_source} ({self.category})"

    @classmethod
    def calculate_total_expenses(cls, project_id):
        total_expenses = cls.objects.filter(project_id=project_id).aggregate(total=Sum('amount'))
        return round(total_expenses['total'] or 0, 2)






from django.db import models
from django.db.models import Sum


class ExpenseCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Expense(models.Model):
    class BudgetSource(models.TextChoices):
        CASH = "CASH", "Cash in Hand"
        ACCOUNT = "ACC", "Account"

    class PaymentStatus(models.TextChoices):
        PAID = "PAID", "Paid"
        UNPAID = "UNPAID", "Unpaid"

    project = models.ForeignKey(
        "project.Project", on_delete=models.CASCADE, related_name="expenses"
    )
    description = models.CharField(max_length=255, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    budget_source = models.CharField(
        max_length=6, choices=BudgetSource.choices, null=True, blank=True
    )
    category = models.ForeignKey(
        ExpenseCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="expenses",
    )
    vendor = models.ForeignKey(
        "vendor.Vendor", on_delete=models.SET_NULL, null=True, related_name="expenses"
    )  # Link to Vendor model
    created_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(
        max_length=6, choices=PaymentStatus.choices, default=PaymentStatus.PAID
    )

    def __str__(self):
        return f"{self.project.project_name} - {self.amount} from {self.budget_source} ({self.category})"

    @classmethod
    def calculate_total_expenses(cls, project_id=None, start_date=None, end_date=None):
        qs = cls.objects.all()
        if project_id:
            qs = qs.filter(project_id=project_id)
        if start_date:
            qs = qs.filter(created_at__gte=start_date)
        if end_date:
            qs = qs.filter(created_at__lte=end_date)
        return qs.aggregate(total=Sum("amount"))["total"] or 0

    class Meta:
        ordering = ["-created_at"]


class JournalExpense(models.Model):

    class BudgetSource(models.TextChoices):
        CASH = "CASH", "Cash in Hand"
        ACCOUNT = "ACC", "Account"

    description = models.CharField(max_length=255, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    budget_source = models.CharField(
        max_length=6, choices=BudgetSource.choices, null=True, blank=True
    )
    category = models.ForeignKey(
        ExpenseCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="journal_expenses",
    )
    vendor = models.ForeignKey(
        "vendor.Vendor",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="journal_expenses",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.description} - {self.amount}"

    class Meta:
        ordering = ["-created_at"]

from django.db import models
from django.utils import timezone

from src.services.project.models import Project


# Create your models here.

class Lender(models.Model):
    name = models.CharField(max_length=255, help_text="Name of the lender")
    email = models.EmailField(help_text="Email address of the lender", blank=True, null=True)
    phone = models.CharField(max_length=20, help_text="Phone number of the lender", blank=True, null=True)
    bic = models.CharField(max_length=11, help_text="BIC of the lender", blank=True, null=True)
    account_number = models.CharField(max_length=20, help_text="Account number of the lender", blank=True, null=True)
    iban = models.CharField(max_length=34, help_text="IBAN of the lender", blank=True, null=True)

    def __str__(self):
        return self.name


class Loan(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="loans")
    lender = models.ForeignKey(Lender, on_delete=models.CASCADE, related_name="loans")
    loan_amount = models.DecimalField(max_digits=12, decimal_places=2, help_text="Total loan amount")
    remaining_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0,
                                           help_text="Remaining loan balance")
    date_issued = models.DateField(default=timezone.now, help_text="Date when the loan was issued")
    due_date = models.DateField(help_text="Due date for loan repayment")
    is_repaid = models.BooleanField(default=False, help_text="Indicates if the loan has been fully repaid")
    reason = models.CharField(max_length=544, blank=True, null=True)

    def save(self, *args, **kwargs):
        # Initialize remaining_amount to loan_amount if it's a new loan
        if not self.pk:
            self.remaining_amount = self.loan_amount
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Loan for {self.project.project_name} from {self.lender.name}"


    def get_total_paid(self):
        return self.loan_amount - self.remaining_amount

    def update_remaining_amount(self, return_amount):
        """Handles repayments and updates remaining balance."""
        self.remaining_amount -= return_amount
        if self.remaining_amount <= 0:
            self.remaining_amount = 0
            self.is_repaid = True
        self.save()


class LoanReturn(models.Model):
    loan = models.ForeignKey(
        Loan,
        on_delete=models.CASCADE,
        related_name="returns",
        help_text="The loan associated with this return."
    )
    return_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    return_date = models.DateTimeField(
        default=timezone.now,
    )
    remarks = models.CharField(
        max_length=500,
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when this return record was created."
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp of the last update to this return record."
    )

    class Meta:
        ordering = ['-return_date']
        verbose_name = "Loan Return"
        verbose_name_plural = "Loan Returns"
        constraints = [
            models.CheckConstraint(
                check=models.Q(return_amount__gt=0),
                name="return_amount_positive"
            )
        ]

    def __str__(self):
        return f"Return of {self.return_amount} on {self.return_date} for Loan ID {self.loan.id}"

    def save(self, *args, **kwargs):
        # Add custom logic if needed, such as validating the return amount
        if self.return_amount > self.loan.remaining_amount:
            raise ValueError("Return amount cannot exceed the remaining loan balance.")
        super().save(*args, **kwargs)

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.db.models import Sum
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField

from src.services.project.models import Project


class Lender(models.Model):
    name = models.CharField(max_length=255, help_text="Name of the lender")
    email = models.EmailField(
        help_text="Email address of the lender", blank=True, null=True
    )
    phone = PhoneNumberField(
        max_length=20,
        help_text="Phone number of the lender",
        blank=True,
        null=True,
        region="PK",
    )
    bank_account = models.CharField(
        max_length=11, help_text="Bank Account of the lender", blank=True, null=True
    )
    account_number = models.CharField(
        max_length=20, help_text="Account number of the lender", blank=True, null=True
    )
    iban = models.CharField(
        max_length=34, help_text="IBAN of the lender", blank=True, null=True
    )

    def __str__(self):
        return self.name

    def get_total_due(self):
        """
        Calculate the total due amount for all loans of this lender.
        """

        misc_loans = (
            self.misc_loans.aggregate(total_due=Sum("remaining_amount"))["total_due"]
            or 0
        )
        loans = (
            self.loans.aggregate(total_due=models.Sum("remaining_amount"))["total_due"]
            or 0
        )

        return round(loans + misc_loans, 2)


class Loan(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="loans")
    lender = models.ForeignKey(Lender, on_delete=models.CASCADE, related_name="loans")

    # Monetary fields
    loan_amount = models.DecimalField(
        max_digits=12, decimal_places=2, help_text="Total loan amount"
    )
    payable_after_interest = models.DecimalField(
        max_digits=12, decimal_places=2, help_text="Payable after interest", null=True
    )
    interest_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Interest rate as a percentage",
        null=True,
    )
    remaining_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        help_text="Remaining loan balance",
    )

    # Dates
    date_issued = models.DateField(
        default=timezone.now, help_text="Date when the loan was issued"
    )
    due_date = models.DateField(help_text="Due date for loan repayment")

    # Status and reason
    is_repaid = models.BooleanField(
        default=False, help_text="Indicates if the loan has been fully repaid"
    )
    reason = models.CharField(max_length=544, blank=True, null=True)

    def save(self, *args, **kwargs):
        self.payable_after_interest = self.calculate_payable_after_interest()

        if not self.pk:
            self.remaining_amount = self.payable_after_interest
        super().save(*args, **kwargs)

    def calculate_payable_after_interest(self):
        """Calculate the total amount payable after applying the interest rate."""
        if self.interest_rate is None:
            return self.loan_amount  # Return loan amount if no interest rate is set
        if self.interest_rate > 0:
            interest = self.loan_amount * (self.interest_rate / 100)
            return self.loan_amount + interest
        return self.loan_amount

    def __str__(self):
        return f"Loan for {self.project.project_name} from {self.lender.name}"

    def get_total_paid(self):
        """Calculate the total amount paid so far."""
        return self.payable_after_interest - self.remaining_amount

    def update_remaining_amount(self, return_amount):
        """Handles repayments and updates remaining balance."""
        self.remaining_amount -= return_amount
        if self.remaining_amount <= 0:
            self.remaining_amount = 0
            self.is_repaid = True
        self.save()

    @classmethod
    def calculate_total_unpaid_amount(cls, project_pk=None):
        """
        Calculate the total unpaid amount for all loans,
        or for loans related to a specific project if project_pk is provided.
        """
        if project_pk is not None:
            total_unpaid = cls.objects.filter(project__pk=project_pk).aggregate(
                total=Sum("remaining_amount")
            )["total"]
        else:
            total_unpaid = cls.objects.aggregate(total=Sum("remaining_amount"))["total"]
        return round(total_unpaid or 0, 2)


class LoanReturn(models.Model):
    loan = models.ForeignKey(
        Loan,
        on_delete=models.CASCADE,
        related_name="returns",
        help_text="The loan associated with this return.",
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
        auto_now_add=True, help_text="Timestamp when this return record was created."
    )
    updated_at = models.DateTimeField(
        auto_now=True, help_text="Timestamp of the last update to this return record."
    )

    class Meta:
        ordering = ["-return_date"]
        verbose_name = "Loan Return"
        verbose_name_plural = "Loan Returns"
        constraints = [
            models.CheckConstraint(
                check=models.Q(return_amount__gt=0), name="return_amount_positive"
            )
        ]

    def __str__(self):
        return f"Return of {self.return_amount} on {self.return_date} for Loan ID {self.loan.id}"


class MiscLoan(models.Model):
    lender = models.ForeignKey(
        Lender, on_delete=models.CASCADE, related_name="misc_loans"
    )

    # Monetary fields
    loan_amount = models.DecimalField(
        max_digits=12, decimal_places=2, help_text="Total loan amount"
    )
    payable_after_interest = models.DecimalField(
        max_digits=12, decimal_places=2, help_text="Payable after interest", null=True
    )
    interest_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Interest rate as a percentage",
        null=True,
    )
    remaining_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        help_text="Remaining loan balance",
    )

    # Dates
    date_issued = models.DateField(
        default=timezone.now, help_text="Date when the loan was issued"
    )
    due_date = models.DateField(help_text="Due date for loan repayment")

    # Status and reason
    is_repaid = models.BooleanField(
        default=False, help_text="Indicates if the loan has been fully repaid"
    )
    reason = models.CharField(max_length=544, blank=True, null=True)

    def save(self, *args, **kwargs):
        self.payable_after_interest = self.calculate_payable_after_interest()
        if not self.pk:
            self.remaining_amount = self.payable_after_interest
        super().save(*args, **kwargs)

    def calculate_payable_after_interest(self):
        """Calculate the total amount payable after applying the interest rate."""
        if self.interest_rate is None:
            return self.loan_amount  # Return loan amount if no interest rate is set
        if self.interest_rate > 0:
            interest = self.loan_amount * (self.interest_rate / 100)
            return self.loan_amount + interest
        return self.loan_amount

    def __str__(self):
        return f"Misc Loan from {self.lender.name}"

    def get_total_paid(self):
        """Calculate the total amount paid so far."""
        return self.payable_after_interest - self.remaining_amount

    def update_remaining_amount(self, return_amount):
        """Handles repayments and updates remaining balance."""
        self.remaining_amount -= return_amount
        if self.remaining_amount <= 0:
            self.remaining_amount = 0
            self.is_repaid = True
        self.save()

    @classmethod
    def calculate_total_unpaid_amount(cls):
        """
        Calculate the total unpaid amount for all loans.
        """
        total_unpaid = cls.objects.aggregate(total=Sum("remaining_amount"))["total"]
        return round(total_unpaid or 0, 2)

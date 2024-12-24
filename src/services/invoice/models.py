from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models, IntegrityError
from django.db.models import Sum
from django.utils import timezone
from num2words import num2words
from phonenumber_field.modelfields import PhoneNumberField

from src.web.dashboard.utils import capitalize_and_replace_currency
from src.services.project.models import Project


class Invoice(models.Model):
    INVOICE_STATUS = (
        ("PENDING", "PENDING"),
        ("PAID", "PAID"),
    )
    invoice_id = models.AutoField(primary_key=True)
    date = models.DateField(default=timezone.now)

    client_name = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255)
    phone = PhoneNumberField(max_length=15, region="PK")
    address = models.CharField(max_length=255)
    email = models.EmailField(max_length=50)

    invoice_number = models.CharField(max_length=100, unique=True, null=True)
    subject = models.CharField(max_length=255)
    notes = models.TextField()

    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_in_words = models.CharField(max_length=255)
    status = models.CharField(max_length=10, choices=INVOICE_STATUS, default="PENDING")
    due_date = models.DateField(default=timezone.now)

    letterhead = models.BooleanField(default=True)

    project = models.ForeignKey(
        Project, related_name="invoices", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    tax = models.BooleanField(default=True, null=True)

    def calculate_total_amount(self):
        total = self.items.aggregate(total=Sum("amount"))["total"] or 0
        self.total_amount = total
        self.total_in_words = capitalize_and_replace_currency(
            num2words(total, to="currency", lang="en_IN")
        )
        self.save(update_fields=["total_amount", "total_in_words"])

    def save(self, *args, **kwargs):
        if not self.pk:
            super().save(*args, **kwargs)

            if not self.invoice_number:
                self.invoice_number = f"INV-{self.pk:06d}"
                try:
                    super().save(update_fields=["invoice_number"])
                except IntegrityError as e:
                    raise IntegrityError(f"Error saving Invoice: {e}")
        else:
            super().save(*args, **kwargs)

    @classmethod
    def calculate_total_received(cls, project_id=None):
        total_receivables = cls.objects.filter(
            project_id=project_id, status="PAID"
        ).aggregate(total=Sum("total_amount"))
        return round(total_receivables["total"] or 0, 2)

    @classmethod
    def calculate_total_receivables(cls, project_id=None):
        if project_id:
            total_receivables = cls.objects.filter(
                project_id=project_id, status="PENDING"
            ).aggregate(total=Sum("total_amount"))
            return round(total_receivables["total"] or 0, 2)
        else:
            total_receivables = cls.objects.filter(status="PENDING").aggregate(
                total=Sum("total_amount")
            )
            return round(total_receivables["total"] or 0, 2)

    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.project.project_name}"

    class Meta:
        ordering = ["-created_at"]


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, related_name="items", on_delete=models.CASCADE)
    item_name = models.CharField(max_length=255)
    description = models.CharField(blank=True, null=True, max_length=500)
    quantity = models.IntegerField(default=1)
    rate = models.DecimalField(max_digits=15, decimal_places=2)  # One Item
    amount = models.DecimalField(
        max_digits=15, decimal_places=2, editable=False
    )  # For all the items (SUMS)
    tax = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=0.0,
        validators=[MinValueValidator(0.00), MaxValueValidator(50.00)],
        null=True,
        blank=True,
    )

    def save(self, *args, **kwargs):
        # Calculate the total amount including tax
        base_amount = self.quantity * self.rate
        tax_amount = base_amount * (self.tax / 100) if self.tax else 0
        self.amount = base_amount + tax_amount

        super().save(*args, **kwargs)
        self.invoice.calculate_total_amount()

    @property
    def display_name(self):
        return f"{self.item_name} - {self.invoice.invoice_number} - {self.invoice.project.project_name}"

    def __str__(self):
        return self.display_name

    def get_total_without_tax(self):
        return self.quantity * self.rate

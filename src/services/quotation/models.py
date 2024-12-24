from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Sum
from django.utils import timezone
from num2words import num2words
from phonenumber_field.modelfields import PhoneNumberField
from src.web.dashboard.utils import capitalize_and_replace_currency

from src.services.project.models import Project


class Quotation(models.Model):
    quotation_id = models.AutoField(primary_key=True)
    date = models.DateField(default=timezone.now)

    client_name = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255)
    phone = PhoneNumberField(max_length=15, region="PK")
    email = models.EmailField(max_length=50)
    address = models.CharField(max_length=255)

    quotation_number = models.CharField(max_length=100, unique=True, null=True)
    subject = models.CharField(max_length=255)
    notes = models.TextField()

    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_in_words = models.CharField(max_length=255)
    due_date = models.DateField(default=timezone.now)

    letterhead = models.BooleanField(default=True)

    project = models.OneToOneField(
        Project, on_delete=models.CASCADE, related_name="quotation"
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

        if not self.quotation_number:
            self.quotation_number = "# QUO-{:06d}".format(self.quotation_id)
        super().save(*args, **kwargs)

    @classmethod
    def calculate_total_received(cls, project_id=None):
        total_received = cls.objects.filter(project_id=project_id).aggregate(
            total=Sum("total_amount")
        )
        return round(total_received["total"] or 0, 2)

    @classmethod
    def calculate_total_quotes(cls, project_id=None):
        if project_id:
            total_quotes = cls.objects.filter(project_id=project_id).aggregate(
                total=Sum("total_amount")
            )
            return round(total_quotes["total"] or 0, 2)
        else:
            total_quotes = cls.objects.all().aggregate(total=Sum("total_amount"))
            return round(total_quotes["total"] or 0, 2)

    def __str__(self):
        return f"Quotation {self.quotation_number} - {self.client_name} - {self.project.project_name}"

    class Meta:
        ordering = ["-created_at"]


class QuotationItem(models.Model):
    quotation = models.ForeignKey(
        Quotation, related_name="items", on_delete=models.CASCADE
    )
    item_name = models.CharField(max_length=255)
    description = models.CharField(blank=True, null=True, max_length=500)
    quantity = models.IntegerField(default=1)
    rate = models.DecimalField(max_digits=15, decimal_places=2)  # One Item
    amount = models.DecimalField(
        max_digits=15, decimal_places=2, editable=False
    )  # For all the items (SUMS)
    tax = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
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
        self.quotation.calculate_total_amount()

    @property
    def display_name(self):
        return f"{self.item_name} - {self.quotation.quotation_number} - {self.quotation.project.project_name}"

    def __str__(self):
        return self.display_name

    def get_total_without_tax(self):
        return self.quantity * self.rate


class QuotationGeneral(models.Model):
    status_choices = [
        ("QUOTE", "Quotation"),
        ("INVOICED", "Invoiced"),
        ("PAID", "Paid"),
    ]
    status = models.CharField(max_length=8, choices=status_choices, default="QUOTE")
    date = models.DateField(default=timezone.now)

    client_name = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255)
    phone = PhoneNumberField(max_length=15, region="PK")
    email = models.EmailField(max_length=50)
    address = models.CharField(max_length=255)

    quotation_number = models.CharField(max_length=100, unique=True, null=True)
    subject = models.CharField(max_length=255)
    notes = models.TextField()

    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_in_words = models.CharField(max_length=255)
    due_date = models.DateField(default=timezone.now)

    letterhead = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    tax = models.BooleanField(default=True, null=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            # Save first to generate the primary key
            super().save(*args, **kwargs)

        if not self.quotation_number:
            self.quotation_number = f"# QUO-{self.pk:06d}"

        if self.status in ["INVOICED", "PAID"] and "QUO" in self.quotation_number:
            self.quotation_number = self.quotation_number.replace("QUO", "INV")

        # Save again after updating the quotation_number
        super().save(*args, **kwargs)

    def calculate_total_amount(self):
        total = self.items.aggregate(total=Sum("amount"))["total"] or 0
        self.total_amount = total
        self.total_in_words = capitalize_and_replace_currency(
            num2words(total, to="currency", lang="en_IN")
        )
        self.save(update_fields=["total_amount", "total_in_words"])


class ItemGeneral(models.Model):
    quotation = models.ForeignKey(
        QuotationGeneral, related_name="items", on_delete=models.CASCADE
    )
    item_name = models.CharField(max_length=255)
    description = models.CharField(blank=True, null=True, max_length=500)
    quantity = models.IntegerField(default=1)
    rate = models.DecimalField(max_digits=15, decimal_places=2)  # One Item
    amount = models.DecimalField(
        max_digits=15, decimal_places=2, editable=False
    )  # For all the items (SUMS)
    tax = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
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
        self.quotation.calculate_total_amount()

    @property
    def display_name(self):
        return f"{self.item_name} - {self.quotation.quotation_number}"

    def __str__(self):
        return self.display_name

    def get_total_without_tax(self):
        return self.quantity * self.rate

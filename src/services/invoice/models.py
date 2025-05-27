from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
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
        self.total_in_words = num2words(total).strip().capitalize() + ' rupees'

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
        from decimal import Decimal, InvalidOperation
        try:
            quantity = Decimal(self.quantity)
            rate = Decimal(self.rate)
            base_amount = quantity * rate

            tax = Decimal(self.tax or 0)
            tax_amount = (base_amount * tax / Decimal("100")).quantize(Decimal("0.01"))
            self.amount = (base_amount + tax_amount).quantize(Decimal("0.01"))

            super().save(*args, **kwargs)
            self.invoice.calculate_total_amount()

        except (InvalidOperation, TypeError, ValueError) as e:
            raise ValueError(f"Invalid decimal operation in InvoiceItem.save(): {e}")

    @property
    def display_name(self):
        return f"{self.item_name} - {self.invoice.invoice_number} - {self.invoice.project.project_name}"

    def __str__(self):
        return self.display_name

    def get_total_without_tax(self):
        return self.quantity * self.rate



class DeliveryChallan(models.Model):
    challan_id = models.AutoField(primary_key=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    invoice = GenericForeignKey("content_type", "object_id")

    date = models.DateField(default=timezone.now)  # Replicate from Invoice.date
    client_name = models.CharField(max_length=255)  # Replicate from Invoice.client_name
    company_name = models.CharField(max_length=255)  # Replicate from Invoice.company_name
    phone = models.CharField(max_length=15)
    address = models.CharField(max_length=255)  # Replicate from Invoice.address
    email = models.EmailField(max_length=50)  # Replicate from Invoice.email
    subject = models.CharField(max_length=255)  # Replicate from Invoice.subject
    notes = models.TextField(blank=True, null=True)  # Replicate from Invoice.notes
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Replicate from Invoice.total_amount
    total_in_words = models.CharField(max_length=255)  # Replicate from Invoice.total_in_words
    delivered_by = models.CharField(max_length=255, blank=True, null=True)
    received_by = models.CharField(max_length=255, blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        """Safely get invoice number if available."""
        if hasattr(self.invoice, "invoice_number"):
            return f"Delivery Challan - {self.invoice.invoice_number}"
        return f"Delivery Challan for {self.invoice.__class__.__name__} #{self.object_id}"

    class Meta:
        ordering = ["-date"]

    def get_item_count(self):
        n=0
        for i in self.items.all():
            n+=i.quantity
        return n


class DeliveryChallanItem(models.Model):
    challan = models.ForeignKey(DeliveryChallan, on_delete=models.CASCADE, related_name="items")

    # Generic Foreign Key for invoice/quotation items
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    invoice_item = GenericForeignKey("content_type", "object_id")

    item_name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    quantity = models.PositiveIntegerField()
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    tax = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)

    def __str__(self):
        return f"{self.item_name} (x{self.quantity})"
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from num2words import num2words

from src.services.project.models import Project


class Quotation(models.Model):
    quotation_id = models.AutoField(primary_key=True)
    date = models.DateField(default=timezone.now)

    client_name = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255)
    phone = models.IntegerField()
    address = models.CharField(max_length=255)

    quotation_number = models.CharField(max_length=100, unique=True, null=True)
    subject = models.CharField(max_length=255)
    notes = models.TextField()

    percent_tax = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0.00)]
    )


    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_in_words = models.CharField(max_length=255)

    project = models.OneToOneField(Project, related_name="quotation", on_delete=models.CASCADE)


    def calculate_total_amount(self):
        total = sum(item.amount for item in self.items.all())
        self.total_amount = total
        self.total_in_words = num2words(total, to="currency", lang="en_IN")
        self.save(update_fields=["total_amount", "total_in_words"])

    def save(self, *args, **kwargs):

        if not self.pk:
            super().save(*args, **kwargs)

        if not self.quotation_number:
            self.quotation_number = '# QT-{:06d}'.format(self.quotation_id)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Quotation {self.quotation_number} - {self.client_name} - {self.project.project_name}"


class QuotationItem(models.Model):
    quotation = models.ForeignKey(Quotation, related_name='items', on_delete=models.CASCADE)
    item_name = models.CharField(max_length=255)
    description = models.CharField(blank=True, null=True, max_length=500)
    quantity = models.IntegerField(default=1)
    rate = models.DecimalField(max_digits=15, decimal_places=2)
    amount = models.DecimalField(max_digits=15, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        # Calculate the amount based on quantity and rate
        self.amount = self.quantity * self.rate
        super().save(*args, **kwargs)
        # Update the total amount in the associated quotation
        self.quotation.calculate_total_amount()
    @property
    def display_name(self):
        return f"{self.item_name} - {self.quotation.quotation_number} - {self.quotation.project.project_name}"

    def __str__(self):
        return self.display_name
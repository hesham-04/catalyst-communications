# Create your models here.
from django.db import models
from django.db.models import Sum
from django.utils import timezone
from num2words import num2words
from src.services.project.models import Project


class Invoice(models.Model):
    invoice_id = models.AutoField(primary_key=True)
    date = models.DateField(default=timezone.now)

    client_name = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=255)

    invoice_number = models.CharField(max_length=100, unique=True, null=True)
    subject = models.CharField(max_length=255)
    notes = models.TextField()

    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_in_words = models.CharField(max_length=255)

    letterhead = models.BooleanField(default=True)

    project = models.ForeignKey(Project, related_name="invoices", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, null=True)


    def calculate_total_amount(self):
        total = sum(item.amount for item in self.items.all())
        self.total_amount = total
        self.total_in_words = num2words(total, to="currency", lang="en_IN")
        self.save(update_fields=["total_amount", "total_in_words"])

    def save(self, *args, **kwargs):
        if not self.pk:
            super().save(*args, **kwargs)

        if not self.invoice_number:
            self.invoice_number = '# INV-{:06d}'.format(self.invoice_id)
        super().save(*args, **kwargs)


    @classmethod
    def calculate_total_receivables(cls, project_id):
        total_receivables = cls.objects.filter(project_id=project_id).aggregate(total=Sum('total_amount'))
        return round(total_receivables['total'] or 0, 2)

    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.client_name} - {self.project.project_name}"

    class Meta:
        ordering=['-created_at']



class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, related_name='items', on_delete=models.CASCADE)
    item_name = models.CharField(max_length=255)
    description = models.CharField(blank=True, null=True, max_length=500)
    quantity = models.IntegerField(default=1)
    rate = models.DecimalField(max_digits=15, decimal_places=2)
    amount = models.DecimalField(max_digits=15, decimal_places=2, editable=False)
    tax = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):
        self.amount = int(self.quantity) * int(self.rate)
        super().save(*args, **kwargs)
        self.invoice.calculate_total_amount()

    @property
    def display_name(self):
        return f"{self.item_name} - {self.invoice.invoice_number} - {self.invoice.project.project_name}"

    def __str__(self):
        return self.display_name


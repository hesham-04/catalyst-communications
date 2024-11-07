from django.db import models
from django.utils import timezone
from num2words import num2words


class Quotation(models.Model):
    quotation_id = models.AutoField(primary_key=True)
    date = models.DateField(default=timezone.now)
    location = models.CharField(max_length=255)
    email = models.EmailField()
    website_link = models.URLField(blank=True, null=True)
    name = models.CharField(max_length=255)
    quotation_number = models.CharField(max_length=100, unique=True)
    subject = models.CharField(max_length=255)
    text = models.TextField()
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, editable=False, default=0.00)
    total_in_words = models.CharField(max_length=500, editable=False, blank=True, null=True)

    def calculate_total_amount(self):
        total = sum(item.amount for item in self.items.all())
        self.total_amount = total
        # Convert total to words (e.g., "two million, three hundred seventy-five thousand rupees only")
        self.total_in_words = num2words(total, to="currency", lang="en", currency="PKR")
        self.save()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.calculate_total_amount()  # Calculate total amount after saving
        if not self.quotation_number:
            self.quotation_number = '# QT-{:06d}'.format(self.quotation_id)
        super().save(*args, **kwargs)



    def _str_(self):
        return f"Quotation {self.quotation_number} - {self.name}"


class QuotationItem(models.Model):
    quotation = models.ForeignKey(Quotation, related_name='items', on_delete=models.CASCADE)
    item_name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1.00)
    rate = models.DecimalField(max_digits=15, decimal_places=2)
    amount = models.DecimalField(max_digits=15, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        # Calculate the amount based on quantity and rate
        self.amount = self.quantity * self.rate
        super().save(*args, **kwargs)
        # Update the total amount in the associated quotation
        self.quotation.calculate_total_amount()

    def _str_(self):
        return f"{self.item_name} - {self.quotation.quotation_number}"
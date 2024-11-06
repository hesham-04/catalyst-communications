from django.db import models


class Invoice(models.Model):
    invoice_number = models.CharField(max_length=100, unique=True)
    date = models.DateField()
    due_date = models.DateField(blank=True, null=True)
    customer = models.ForeignKey('Customer.Customer', on_delete=models.CASCADE)
    project = models.ForeignKey('Project.Project', on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, editable=False, default=0.00)

    def __str__(self):
        return f"Invoice {self.invoice_number} for  {self.customer} - {self.project}"


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    description = models.TextField(blank=True, null=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1.00)
    rate = models.DecimalField(max_digits=15, decimal_places=2)
    amount = models.DecimalField(max_digits=15, decimal_places=2, editable=False)
    tax = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        # Calculate total price with tax
        self.total_price = self.rate * self.quantity * (1 + self.tax / 100)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.description}" - f"{self.total_price}"

from django.db import models

class Customer(models.Model):
    CUSTOMER_TYPE_CHOICES = [
        ('business', 'Business'),
        ('individual', 'Individual'),
    ]
    CURRENCY_CHOICES = [
        ('USD', 'US Dollar'),
        ('EUR', 'Euro'),
        ('PKR', 'Pakistani Rupee'),
    ]
    PAYMENT_DUE_CHOICES = [
        ('net_15', 'Net 15'),
        ('net_45', 'Net 45'),
        ('net_60', 'Net 60'),
        ('due_receipt', 'Due On Receipt'),
        ('due_eom', 'Due End of Month'),
    ]
    salutation = models.CharField(max_length=10, choices=[('Mr.', 'Mr.'), ('Ms.', 'Ms.'), ('Mrs.', 'Mrs.')],
                                  default='Mr.')
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    company_name = models.CharField(max_length=100, blank=True)
    customer_type = models.CharField(max_length=10, choices=CUSTOMER_TYPE_CHOICES, default='business')
    email = models.EmailField()
    phone = models.IntegerField(blank=True, )
    # work_phone = models.IntegerField(blank=True)
    # mobile = models.CharField(max_length=15, blank=True)
    other_details = models.TextField(blank=True)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='PKR')
    payment_due_period = models.CharField(max_length=15, choices=PAYMENT_DUE_CHOICES, default='due_eom')
    company_id = models.CharField(max_length=50, unique=True, blank=True, null=True)


    def get_full_name(self):
        return f"{self.salutation} {self.first_name} {self.last_name}"

    def __str__(self):
        return f"{self.salutation} {self.first_name} {self.last_name}"



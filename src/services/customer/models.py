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
    salutation = models.CharField(max_length=10, choices=[('Mr.', 'Mr.'), ('Ms.', 'Ms.'), ('Mrs.', 'Mrs.')])
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    company_name = models.CharField(max_length=100, blank=True)
    display_name = models.CharField(max_length=100)
    customer_type = models.CharField(max_length=10, choices=CUSTOMER_TYPE_CHOICES)
    email = models.EmailField()
    phone = models.CharField(max_length=15, blank=True)
    work_phone = models.CharField(max_length=15, blank=True)
    mobile = models.CharField(max_length=15, blank=True)
    other_details = models.TextField(blank=True)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES)


    def __str__(self):
        return self.display_name



class ContactPerson(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='contact_persons')
    salutation = models.CharField(max_length=10, choices=[('Mr.', 'Mr.'), ('Ms.', 'Ms.'), ('Mrs.', 'Mrs.')])
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    work_phone = models.CharField(max_length=15, blank=True)
    mobile = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return f"{self.salutation} {self.first_name} {self.last_name}"
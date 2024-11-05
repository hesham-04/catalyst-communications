# Generated by Django 5.1.2 on 2024-11-04 15:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0004_alter_customer_payment_due_period'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='currency',
            field=models.CharField(choices=[('USD', 'US Dollar'), ('EUR', 'Euro'), ('PKR', 'Pakistani Rupee')], default='PKR', max_length=3),
        ),
        migrations.AlterField(
            model_name='customer',
            name='customer_type',
            field=models.CharField(choices=[('business', 'Business'), ('individual', 'Individual')], default='business', max_length=10),
        ),
        migrations.AlterField(
            model_name='customer',
            name='salutation',
            field=models.CharField(choices=[('Mr.', 'Mr.'), ('Ms.', 'Ms.'), ('Mrs.', 'Mrs.')], default='Mr.', max_length=10),
        ),
    ]
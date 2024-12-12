# Generated by Django 5.1.3 on 2024-12-07 17:00

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoice', '0010_alter_invoice_phone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoiceitem',
            name='tax',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=5, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(50.0)]),
        ),
    ]
# Generated by Django 5.1.2 on 2024-11-07 18:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quotation', '0004_alter_quotation_quotation_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quotationitem',
            name='description',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]

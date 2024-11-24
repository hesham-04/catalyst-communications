# Generated by Django 5.1.2 on 2024-11-23 00:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendor', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vendor',
            name='currency',
            field=models.CharField(choices=[('USD', 'US Dollar'), ('EUR', 'Euro'), ('PKR', 'Pakistani Rupee')], default='USD', max_length=3),
        ),
    ]
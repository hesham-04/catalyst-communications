# Generated by Django 5.1.2 on 2024-11-06 16:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0005_remove_lender_contact_info_remove_lender_iban_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='loan',
            name='lender',
        ),
        migrations.RemoveField(
            model_name='loan',
            name='project',
        ),
        migrations.DeleteModel(
            name='Lender',
        ),
        migrations.DeleteModel(
            name='Loan',
        ),
    ]

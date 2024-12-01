# Generated by Django 5.1.2 on 2024-11-29 09:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loan', '0002_loan_interest_rate_alter_loan_payable_after_interest'),
    ]

    operations = [
        migrations.AlterField(
            model_name='loan',
            name='interest_rate',
            field=models.DecimalField(decimal_places=2, help_text='Interest rate as a percentage', max_digits=5, null=True),
        ),
    ]

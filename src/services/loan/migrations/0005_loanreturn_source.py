# Generated by Django 5.1.2 on 2024-11-26 00:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loan', '0004_loan_reason'),
    ]

    operations = [
        migrations.AddField(
            model_name='loanreturn',
            name='source',
            field=models.CharField(choices=[('CASH', 'Cash in Hand'), ('ACC', 'Account')], max_length=6, null=True),
        ),
    ]
# Generated by Django 5.1.2 on 2024-11-28 23:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transaction', '0006_alter_ledger_options_alter_ledger_transaction_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ledger',
            name='transaction_type',
            field=models.CharField(choices=[('BUDGET_ASSIGN', 'Budget Assigned to Project'), ('TRANSFER', 'Funds Transfer'), ('CREATE_LOAN', 'Loan Created'), ('RETURN_LOAN', 'Loan Returned'), ('CREATE_EXPENSE', 'Expense Created'), ('MISC_EXPENSE', 'Journal Expense Created'), ('INVOICE_PAYMENT', 'Invoice Paid')], max_length=50),
        ),
    ]

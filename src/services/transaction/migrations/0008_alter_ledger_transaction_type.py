# Generated by Django 5.1.2 on 2024-11-29 17:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transaction', '0007_alter_ledger_transaction_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ledger',
            name='transaction_type',
            field=models.CharField(choices=[('BUDGET_ASSIGN', 'Budget Assigned to Project'), ('TRANSFER', 'Funds Transfer'), ('CREATE_LOAN', 'Loan Created'), ('RETURN_LOAN', 'Loan Returned'), ('CREATE_EXPENSE', 'Expense Created'), ('CREATE_JOURNAL_EXPENSE', 'Journal Expense Created'), ('ADD_CASH', 'Added Cash'), ('INVOICE_PAYMENT', 'Invoice Paid')], max_length=50),
        ),
    ]
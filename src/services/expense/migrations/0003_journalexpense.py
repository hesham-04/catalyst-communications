# Generated by Django 5.1.2 on 2024-11-28 08:45

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('expense', '0002_alter_expense_payment_status'),
        ('vendor', '0002_alter_vendor_currency'),
    ]

    operations = [
        migrations.CreateModel(
            name='JournalExpense',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(blank=True, max_length=255, null=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('budget_source', models.CharField(blank=True, choices=[('CASH', 'Cash in Hand'), ('ACC', 'Account')], max_length=6, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='journal_expenses', to='expense.expensecategory')),
                ('vendor', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='journal_expenses', to='vendor.vendor')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
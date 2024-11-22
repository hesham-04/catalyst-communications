# Generated by Django 5.1.2 on 2024-11-08 16:21

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('expense', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExpenseCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.AlterField(
            model_name='expense',
            name='budget_source',
            field=models.CharField(choices=[('CASH', 'Cash in Hand'), ('ACC', 'Account'), ('CLIENT', 'Client Provided'), ('LOAN', 'Project Loan')], max_length=6),
        ),
        migrations.AddField(
            model_name='expense',
            name='category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='expenses', to='expense.expensecategory'),
        ),
    ]
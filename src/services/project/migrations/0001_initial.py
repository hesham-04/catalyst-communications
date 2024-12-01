# Generated by Django 5.1.2 on 2024-11-05 19:59

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('customer', '0005_alter_customer_currency_alter_customer_customer_type_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project_name', models.CharField(blank=True, help_text='Name of the project', max_length=255)),
                ('description', models.TextField(blank=True, help_text='Description of the project', null=True)),
                ('project_budget', models.DecimalField(decimal_places=2, default=0.0, help_text='Assigned project budget', max_digits=12)),
                ('client_funds_received', models.DecimalField(decimal_places=2, default=0.0, help_text='Total funds provided by the client', max_digits=12)),
                ('project_status', models.CharField(choices=[('QT', 'Quotation'), ('AW', 'Awaiting Approval'), ('CL', 'Cancelled'), ('IP', 'In Progress'), ('FN', 'Finished')], default='QT', help_text='Current status of the project', max_length=2)),
                ('budget_source', models.CharField(choices=[('BANK', 'Bank'), ('CASH', 'Cash in Hand'), ('ACC', 'Account'), ('CLIENT', 'Client Provided')], default='CASH', help_text='Source of the project budget', max_length=6)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='projects', to='customer.customer')),
            ],
        ),
    ]

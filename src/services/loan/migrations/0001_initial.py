# Generated by Django 5.1.2 on 2024-11-29 09:44

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('project', '0014_remove_project_client_funds_received_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Lender',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Name of the lender', max_length=255)),
                ('email', models.EmailField(blank=True, help_text='Email address of the lender', max_length=254, null=True)),
                ('phone', models.CharField(blank=True, help_text='Phone number of the lender', max_length=20, null=True)),
                ('bic', models.CharField(blank=True, help_text='BIC of the lender', max_length=11, null=True)),
                ('account_number', models.CharField(blank=True, help_text='Account number of the lender', max_length=20, null=True)),
                ('iban', models.CharField(blank=True, help_text='IBAN of the lender', max_length=34, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Loan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('loan_amount', models.DecimalField(decimal_places=2, help_text='Total loan amount', max_digits=12)),
                ('payable_after_interest', models.DecimalField(decimal_places=2, help_text='Payable after interest', max_digits=12)),
                ('remaining_amount', models.DecimalField(decimal_places=2, default=0, help_text='Remaining loan balance', max_digits=12)),
                ('date_issued', models.DateField(default=django.utils.timezone.now, help_text='Date when the loan was issued')),
                ('due_date', models.DateField(help_text='Due date for loan repayment')),
                ('is_repaid', models.BooleanField(default=False, help_text='Indicates if the loan has been fully repaid')),
                ('reason', models.CharField(blank=True, max_length=544, null=True)),
                ('lender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='loans', to='loan.lender')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='loans', to='project.project')),
            ],
        ),
        migrations.CreateModel(
            name='LoanReturn',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('return_amount', models.DecimalField(decimal_places=2, max_digits=12)),
                ('source', models.CharField(choices=[('CASH', 'Cash in Hand'), ('ACC', 'Account')], max_length=6, null=True)),
                ('return_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('remarks', models.CharField(blank=True, max_length=500, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='Timestamp when this return record was created.')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='Timestamp of the last update to this return record.')),
                ('loan', models.ForeignKey(help_text='The loan associated with this return.', on_delete=django.db.models.deletion.CASCADE, related_name='returns', to='loan.loan')),
            ],
            options={
                'verbose_name': 'Loan Return',
                'verbose_name_plural': 'Loan Returns',
                'ordering': ['-return_date'],
                'constraints': [models.CheckConstraint(condition=models.Q(('return_amount__gt', 0)), name='return_amount_positive')],
            },
        ),
    ]

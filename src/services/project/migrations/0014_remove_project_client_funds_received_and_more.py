# Generated by Django 5.1.2 on 2024-11-21 08:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0013_alter_project_budget_source'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='client_funds_received',
        ),
        migrations.RemoveField(
            model_name='project',
            name='project_budget',
        ),
        migrations.RemoveField(
            model_name='project',
            name='project_client_fund',
        ),
        migrations.RemoveField(
            model_name='project',
            name='project_loan_recieved',
        ),
    ]
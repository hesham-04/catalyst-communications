# Generated by Django 5.1.2 on 2024-11-06 16:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0006_remove_loan_lender_remove_loan_project_delete_lender_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='project_loan_recieved',
            field=models.DecimalField(decimal_places=2, default=0.0, help_text='Total loan amount received by the project', max_digits=12),
        ),
    ]
# Generated by Django 5.1.2 on 2024-11-08 16:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0010_alter_project_project_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='budget_source',
            field=models.CharField(choices=[('CASH', 'Cash in Hand'), ('ACC', 'Account'), ('CLIENT', 'Client Provided')], default='CASH', help_text='Source of the project budget', max_length=6),
        ),
    ]

# Generated by Django 5.1.2 on 2024-11-09 07:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0011_alter_project_budget_source'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='total_budget_assigned',
            field=models.DecimalField(decimal_places=2, default=0.0, help_text='Total cumulative budget assigned to the project', max_digits=12),
        ),
    ]

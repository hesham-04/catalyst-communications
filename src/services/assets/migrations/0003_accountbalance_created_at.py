# Generated by Django 5.1.2 on 2024-11-29 17:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0002_delete_journalexpense'),
    ]

    operations = [
        migrations.AddField(
            model_name='accountbalance',
            name='created_at',
            field=models.DateField(auto_now_add=True, null=True),
        ),
    ]

# Generated by Django 5.1.2 on 2024-10-30 11:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tax',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('rate', models.DecimalField(decimal_places=2, max_digits=5)),
                ('is_compound', models.BooleanField(default=False)),
            ],
        ),
    ]
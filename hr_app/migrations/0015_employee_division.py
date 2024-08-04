# Generated by Django 5.0.7 on 2024-07-31 04:18

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hr_app', '0014_employee_station'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='division',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='hr_app.division', verbose_name='Division'),
        ),
    ]

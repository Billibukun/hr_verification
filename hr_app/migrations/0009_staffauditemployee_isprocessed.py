# Generated by Django 5.0.7 on 2024-07-30 11:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hr_app', '0008_rename_educationinfoupdated_employee_iseducationinfoupdated_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='staffauditemployee',
            name='isProcessed',
            field=models.BooleanField(default=False),
        ),
    ]
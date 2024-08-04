# Generated by Django 5.0.7 on 2024-08-04 14:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hr_app', '0016_customreport_reportschedule'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='isEducationInfoApproved',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='employee',
            name='isEmploymentInfoApproved',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='employee',
            name='isFinancialInfoApproved',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='employee',
            name='isNextOfKinInfoApproved',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='employee',
            name='isPassportApproved',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='employee',
            name='isPersonalInfoApproved',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='employee',
            name='isPreviousEmploymentApproved',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='employee',
            name='isSpouseInfoApproved',
            field=models.BooleanField(default=False),
        ),
    ]

# Generated by Django 5.0.7 on 2024-08-07 00:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hr_app', '0024_alter_staffauditemployee_nok1_relationship_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='role',
            field=models.CharField(choices=[('DRUID_VIEWER', 'Druid Viewer'), ('SUPER_ADMIN', 'Super Admin'), ('HR_ADMIN', 'HR Admin'), ('DIRECTOR_GENERAL', 'Director General'), ('DIRECTOR', 'Director'), ('HFC', 'Honourable Federal Commissioner'), ('IT_ADMIN', 'IT Admin'), ('MONITORING_OFFICER', 'Monitoring Officer'), ('TEAMLEAD', 'Teamlead'), ('VERIFICATION_OFFICER', 'Verification Officer'), ('HELPDESK', 'Helpdesk'), ('HR_DATA_SCREENING', 'HR Data Screening')], max_length=20),
        ),
    ]

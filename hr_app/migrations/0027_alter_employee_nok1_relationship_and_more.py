# Generated by Django 5.0.7 on 2024-08-07 02:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hr_app', '0026_alter_userprofile_role'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='nok1_relationship',
            field=models.CharField(blank=True, choices=[('SPOUSE', 'Spouse'), ('CHILD', 'Child'), ('PARENT', 'Parent'), ('SIBLING', 'Sibling'), ('OTHER', 'Other')], max_length=50, null=True, verbose_name='Next of Kin 1 Relationship'),
        ),
        migrations.AlterField(
            model_name='employee',
            name='nok2_relationship',
            field=models.CharField(blank=True, choices=[('SPOUSE', 'Spouse'), ('CHILD', 'Child'), ('PARENT', 'Parent'), ('SIBLING', 'Sibling'), ('OTHER', 'Other')], max_length=50, null=True, verbose_name='Next of Kin 2 Relationship'),
        ),
    ]

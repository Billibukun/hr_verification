# Generated by Django 5.0.7 on 2024-08-06 09:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hr_app', '0020_staffauditemployee_residentialaddress_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='staffauditemployee',
            name='nok1_address',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Next of Kin 1 Address'),
        ),
        migrations.AlterField(
            model_name='staffauditemployee',
            name='nok1_name',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Next of Kin 1 Name'),
        ),
        migrations.AlterField(
            model_name='staffauditemployee',
            name='nok1_phoneNumber',
            field=models.CharField(blank=True, max_length=11, null=True, verbose_name='Next of Kin 1 Phone Number'),
        ),
        migrations.AlterField(
            model_name='staffauditemployee',
            name='nok1_relationship',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Next of Kin 1 Relationship'),
        ),
        migrations.AlterField(
            model_name='staffauditemployee',
            name='nok2_address',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Next of Kin 2 Address'),
        ),
        migrations.AlterField(
            model_name='staffauditemployee',
            name='nok2_name',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Next of Kin 2 Name'),
        ),
        migrations.AlterField(
            model_name='staffauditemployee',
            name='nok2_phoneNumber',
            field=models.CharField(blank=True, max_length=11, null=True, verbose_name='Next of Kin 2 Phone Number'),
        ),
        migrations.AlterField(
            model_name='staffauditemployee',
            name='nok2_relationship',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Next of Kin 2 Relationship'),
        ),
    ]
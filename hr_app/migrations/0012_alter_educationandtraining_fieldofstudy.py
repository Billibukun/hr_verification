# Generated by Django 5.0.7 on 2024-07-30 19:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hr_app', '0011_educationandtraining_fieldofstudy_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='educationandtraining',
            name='fieldOfStudy',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Field of Study'),
        ),
    ]
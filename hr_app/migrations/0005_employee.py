# Generated by Django 5.0.7 on 2024-07-29 22:13

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hr_app', '0004_bank_pfa_staffauditemployee_staffauditeducation'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ippisNumber', models.CharField(max_length=8, unique=True, verbose_name='IPPIS Number')),
                ('fileNumber', models.CharField(blank=True, max_length=7, null=True, verbose_name='File Number')),
                ('nin', models.CharField(blank=True, max_length=11, null=True, unique=True, verbose_name='National Identification Number')),
                ('firstName', models.CharField(blank=True, max_length=50, verbose_name='First Name')),
                ('lastName', models.CharField(blank=True, max_length=50, verbose_name='Surname')),
                ('middleName', models.CharField(blank=True, max_length=50, verbose_name='Middle Name')),
                ('dateOfBirth', models.DateField(blank=True, null=True, verbose_name='Date of Birth')),
                ('gender', models.CharField(blank=True, choices=[('M', 'Male'), ('F', 'Female')], max_length=1, verbose_name='Gender')),
                ('maritalStatus', models.CharField(blank=True, choices=[('S', 'Single'), ('M', 'Married'), ('D', 'Divorced'), ('W', 'Widowed')], max_length=1, verbose_name='Marital Status')),
                ('phoneNumber', models.CharField(blank=True, max_length=15, verbose_name='Phone Number')),
                ('emailAddress', models.EmailField(blank=True, max_length=254, null=True, unique=True, verbose_name='Email Address')),
                ('residentialAddress', models.TextField(blank=True, verbose_name='Residential Address')),
                ('dateOfFirstAppointment', models.DateField(blank=True, null=True, verbose_name='Date of First Appointment')),
                ('dateOfPresentAppointment', models.DateField(blank=True, null=True, verbose_name='Date of Present Appointment')),
                ('dateOfConfirmation', models.DateField(blank=True, null=True, verbose_name='Date of Confirmation')),
                ('cadre', models.CharField(blank=True, choices=[('O', 'OFFICER'), ('E', 'EXECUTIVE'), ('S', 'SECRETARIAL'), ('C', 'CLERICAL'), ('D', 'DRIVER')], help_text='Select your cadre. Officers are those that have a BSC Degree and above. Executives are those that have Higher National Diploma and below', max_length=1, null=True, verbose_name='Cadre')),
                ('currentStep', models.PositiveIntegerField(blank=True, null=True, verbose_name='Current Step')),
                ('passport', models.ImageField(blank=True, null=True, upload_to='employee_passports/', verbose_name='Passport Photo')),
                ('lastPromotionDate', models.DateField(blank=True, null=True, verbose_name='Last Promotion Date')),
                ('isUnderDisciplinaryAction', models.BooleanField(default=False, verbose_name='Under Disciplinary Action')),
                ('isProfileUpdated', models.BooleanField(default=False, verbose_name='Profile Updated')),
                ('profileUpdateDate', models.DateTimeField(blank=True, null=True, verbose_name='Profile Update Date')),
                ('retirementDate', models.DateField(blank=True, null=True, verbose_name='Retirement Date')),
                ('isOnLeave', models.BooleanField(default=False, verbose_name='Is On Leave')),
                ('accountType', models.CharField(blank=True, choices=[('S', 'Savings'), ('C', 'Current')], max_length=1, null=True)),
                ('accountNumber', models.CharField(blank=True, max_length=10, null=True, validators=[django.core.validators.RegexValidator('^\\d{10}$')])),
                ('pfaNumber', models.CharField(blank=True, max_length=15)),
                ('nok1_fullName', models.CharField(blank=True, max_length=100, null=True, verbose_name='Next of Kin 1 Full Name')),
                ('nok1_relationship', models.CharField(blank=True, choices=[('SPOUSE', 'Spouse'), ('CHILD', 'Child'), ('PARENT', 'Parent'), ('SIBLING', 'Sibling'), ('OTHER', 'Other')], max_length=20, null=True, verbose_name='Next of Kin 1 Relationship')),
                ('nok1_address', models.TextField(blank=True, null=True, verbose_name='Next of Kin 1 Address')),
                ('nok1_phoneNumber', models.CharField(blank=True, max_length=11, null=True, validators=[django.core.validators.RegexValidator('^(080|081|090|091|070)\\d{8}$')], verbose_name='Next of Kin 1 Phone Number')),
                ('nok2_fullName', models.CharField(blank=True, max_length=100, null=True, verbose_name='Next of Kin 2 Full Name')),
                ('nok2_relationship', models.CharField(blank=True, choices=[('SPOUSE', 'Spouse'), ('CHILD', 'Child'), ('PARENT', 'Parent'), ('SIBLING', 'Sibling'), ('OTHER', 'Other')], max_length=20, null=True, verbose_name='Next of Kin 2 Relationship')),
                ('nok2_address', models.TextField(blank=True, null=True, verbose_name='Next of Kin 2 Address')),
                ('nok2_phoneNumber', models.CharField(blank=True, max_length=11, null=True, validators=[django.core.validators.RegexValidator('^(080|081|090|091|070)\\d{8}$')], verbose_name='Next of Kin 2 Phone Number')),
                ('spouse_fullName', models.CharField(blank=True, max_length=100, null=True, verbose_name='Spouse Full Name')),
                ('spouse_occupation', models.CharField(blank=True, max_length=100, null=True, verbose_name='Spouse Occupation')),
                ('spouse_employerName', models.CharField(blank=True, max_length=100, null=True, verbose_name='Spouse Employer Name')),
                ('spouse_employmentPeriod', models.CharField(blank=True, max_length=50, null=True, verbose_name='Spouse Employment Period')),
                ('createdAt', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('updatedAt', models.DateTimeField(auto_now=True, verbose_name='Updated At')),
                ('personalInfoUpdated', models.BooleanField(default=False)),
                ('employmentInfoUpdated', models.BooleanField(default=False)),
                ('educationInfoUpdated', models.BooleanField(default=False)),
                ('financialInfoUpdated', models.BooleanField(default=False)),
                ('nextOfKinUpdated', models.BooleanField(default=False)),
                ('spouseInfoUpdated', models.BooleanField(default=False)),
                ('bank', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='hr_app.bank')),
                ('currentGradeLevel', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='hr_app.gradelevel', verbose_name='Current Grade Level')),
                ('department', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='hr_app.department', verbose_name='Department')),
                ('lgaOfOrigin', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='employeesOrigin', to='hr_app.lga', verbose_name='LGA of Origin')),
                ('pfa', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='hr_app.pfa')),
                ('presentAppointment', models.ForeignKey(blank=True, help_text='Select your Present Appointment', null=True, on_delete=django.db.models.deletion.PROTECT, to='hr_app.officialappointment', verbose_name='Present Appointment')),
                ('stateOfOrigin', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='employeesOrigin', to='hr_app.state', verbose_name='State of Origin')),
                ('stateOfPosting', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='employeesPosting', to='hr_app.state', verbose_name='State of Posting')),
                ('updatedBy', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='employeeUpdates', to=settings.AUTH_USER_MODEL, verbose_name='Updated By')),
            ],
            options={
                'verbose_name': 'Employee',
                'verbose_name_plural': 'Employees',
                'ordering': ['lastName', 'firstName'],
            },
        ),
    ]

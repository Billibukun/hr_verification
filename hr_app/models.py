from django.utils import timezone
from datetime import date, datetime, timedelta
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import *
from django.dispatch import *
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.forms import ValidationError


# Create your models here.
class UserProfile(models.Model):
    USER_ROLES = [
        ('DRUID_VIEWER', 'Druid Viewer'),
        ('SUPER_ADMIN', 'Super Admin'),
        ('DIRECTOR_GENERAL', 'Director General'),
        ('IT_ADMIN', 'IT Admin'),
        ('HR_ADMIN', 'HR Admin'),
        ('MONITORING_OFFICER', 'Monitoring Officer'),
        ('VERIFICATION_OFFICER', 'Verification Officer'),
        ('HELPDESK', 'Helpdesk'),
        ('HR_DATA_SCREENING', 'HR Data Screening'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=USER_ROLES)
    phoneNumber = models.CharField(max_length=11, blank=True)
    ippisNumber = models.CharField(max_length=8, unique=True, null=True, blank=True)
    department = models.ForeignKey('Department', on_delete=models.SET_NULL, null=True, blank=True)
    stateOfPosting = models.ForeignKey('State', on_delete=models.SET_NULL, null=True, blank=True, related_name='posting_users')
    allowedStates = models.ManyToManyField('State', blank=True, related_name='allowed_users')
    allowedZones = models.ManyToManyField('Zone', blank=True, related_name='allowed_users')
    allowedDepartments = models.ManyToManyField('Department', blank=True, related_name='allowed_users')

    def __str__(self):
        return f"{self.user.username}'s profile - {self.get_role_display()}"

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    instance.userprofile.save()


class Zone(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=10, unique=True, primary_key=True)

    def __str__(self):
        return self.name


class State(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=3, unique=True, primary_key=True)
    zone = models.ForeignKey(Zone, on_delete=models.PROTECT)

    def __str__(self):
        return self.name


class LGA(models.Model):
    name = models.CharField(max_length=100)
    state = models.ForeignKey(State, on_delete=models.PROTECT)
    code = models.CharField(max_length=5, unique=True, primary_key=True)

    def __str__(self):
        return f"{self.name}, {self.state.name}"


class Department(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True, primary_key=True)

    def __str__(self):
        return self.name


class Division(models.Model):
    code = models.CharField(max_length=7, unique=True, primary_key=True)
    name = models.CharField(max_length=50)
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, related_name="divisions")

    def __str__(self):
        return f"{self.name} ({self.department.name})"

    class Meta:
        ordering = ['code']


class GradeLevel(models.Model):
    level = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(17)],
        primary_key=True)
    name = models.CharField(max_length=20)
    description = models.CharField(max_length=40, blank=True)
    perDiem = models.DecimalField(max_digits=8, decimal_places=2)
    localRunning = models.DecimalField(max_digits=8, decimal_places=2)
    estacode = models.DecimalField(max_digits=8, decimal_places=2)
    assumptionOfDuty = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.name}"


class OfficialAppointment(models.Model):
    CADRE_CHOICES = [
        ('O', 'OFFICER'),
        ('E', 'EXECUTIVE'),
        ('S', 'SECRETARIAL'),
        ('C', 'CLERICAL'),
        ('D', 'DRIVER'),
    ]
    code = models.CharField(max_length=15, unique=True, primary_key=True)
    name = models.CharField(max_length=50)
    gradeLevel = models.ForeignKey(GradeLevel, on_delete=models.CASCADE)
    cadre = models.CharField(max_length=1, choices=CADRE_CHOICES)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Official Appointment"
        verbose_name_plural = "Official Appointments"

class Bank(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=3, unique=True)

    def __str__(self):
        return self.name


class PFA(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=3, unique=True)

    def __str__(self):
        return self.name


class Discrepancy(models.Model):
    DISCREPANCY_TYPES = [
        ('DOB', 'Date of Birth'),
        ('DOF', 'Date of First Appointment'),
        ('DOP', 'Date of Present Appointment'),
        ('DOC', 'Date of Confirmation'),
        ('GL', 'Grade Level'),
        ('DEPT', 'Department'),
        ('SOP', 'State of Posting'),
        ('OTHER', 'Other'),
    ]

    employee = models.ForeignKey(
        'Employee', on_delete=models.CASCADE, related_name='discrepancies')
    discrepancyType = models.CharField(max_length=5, choices=DISCREPANCY_TYPES)
    auditValue = models.CharField(
        max_length=255, help_text="Value from StaffAuditEmployee")
    employeeValue = models.CharField(
        max_length=255, help_text="Value from Employee")
    description = models.TextField(
        blank=True, help_text="Additional details about the discrepancy")
    resolution = models.TextField(blank=True)
    isResolved = models.BooleanField(default=False)
    resolvedBy = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolvedDiscrepancies')
    resolutionDate = models.DateTimeField(null=True, blank=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.employee.ippisNumber} - {self.get_discrepancyType_display()} Discrepancy"

    class Meta:
        verbose_name_plural = "Discrepancies"

def getDifference(self):
        if self.discrepancyType in ['DOB', 'DOF', 'DOP', 'DOC']:
            try:
                audit_date = datetime.strptime(self.auditValue, "%Y-%m-%d").date() if self.auditValue else None
                employee_date = datetime.strptime(self.employeeValue, "%Y-%m-%d").date() if self.employeeValue else None
                
                if audit_date and employee_date:
                    difference = abs((audit_date - employee_date).days)
                    return f"{difference} days"
                elif audit_date and not employee_date:
                    return "Employee value missing"
                elif employee_date and not audit_date:
                    return "Audit value missing"
                else:
                    return "Both values missing"
            except ValueError:
                return "Invalid date format"
        return "N/A"

class StaffAuditEmployee(models.Model):
    ippisNumber = models.CharField(max_length=8, null=True, blank=True)
    fileNumber = models.CharField(max_length=8, null=True, blank=True)
    title = models.CharField(max_length=15)
    surname = models.CharField(max_length=50)
    otherNames = models.CharField(max_length=50)
    dateOfBirth = models.DateField(null=True, blank=True)
    sex = models.CharField(max_length=1, choices=(
        ('M', 'MALE'), ('F', 'FEMALE')))
    stateOfOrigin = models.ForeignKey(
        State, on_delete=models.CASCADE, null=True, blank=True, related_name="state_of_origin")
    lgaOfOrigin = models.ForeignKey(LGA, on_delete=models.CASCADE, null=True, blank=True,
                                    related_name='lga_of_origin')
    MARITAL_CHOICES = [
        ('S', 'SINGLE'),
        ('M', 'MARRIED'),
        ('D', 'DIVORCED'),
        ('W', 'WIDOWED'),
    ]
    maritalStatus = models.CharField(
        max_length=1, choices=MARITAL_CHOICES, null=True, blank=True)
    phoneNumber = models.CharField(max_length=11, null=True, blank=True)

    # Employment Details
    gradeLevel = models.ForeignKey(
        GradeLevel, on_delete=models.CASCADE, null=True, blank=True)
    step = models.IntegerField(null=True, blank=True, validators=[
                               MinValueValidator(1), MaxValueValidator(17)])
    cadre = models.CharField(
        max_length=1, choices=OfficialAppointment.CADRE_CHOICES, null=True, blank=True)
    dateOfFirstAppointment = models.DateField(null=True, blank=True)
    dateOfPresentAppointment = models.DateField(null=True, blank=True)
    dateOfConfirmation = models.DateField(null=True, blank=True)
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, null=True, blank=True)
    stateOfPosting = models.ForeignKey(
        State, on_delete=models.CASCADE, null=True, blank=True, related_name='state_of_posting')
    station = models.ForeignKey(LGA, on_delete=models.CASCADE, null=True, blank=True,
                                related_name='station')
    isOnLeave = models.BooleanField(default=False)

    # Fnancials
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE, null=True, blank=True)
    accountNumber = models.CharField(max_length=10, null=True, blank=True)
    ACCOUNT_TYPES = [
        ('S', 'Savings'),
        ('C', 'Current'),
    ]
    accountType = models.CharField(
        max_length=1, choices=ACCOUNT_TYPES, null=True, blank=True)
    pfa = models.ForeignKey(PFA, on_delete=models.CASCADE, null=True, blank=True)
    pfaNumber = models.CharField(max_length=10, null=True, blank=True)
    branch = models.CharField(max_length=50, null=True, blank=True)

    # Next of Kin
    nok1_name = models.CharField(max_length=50, null=True, blank=True)
    nok1_relationship = models.CharField(max_length=50, null=True, blank=True)
    nok1_address = models.CharField(max_length=100, null=True, blank=True)
    nok1_phoneNumber = models.CharField(max_length=11, null=True, blank=True)
    nok2_name = models.CharField(max_length=50, null=True, blank=True)
    nok2_relationship = models.CharField(max_length=50, null=True, blank=True)
    nok2_address = models.CharField(max_length=100, null=True, blank=True)
    nok2_phoneNumber = models.CharField(max_length=11, null=True, blank=True)

    # Control Fieldss
    isProcessed = models.BooleanField(default=False)
    staffUpdate = models.BooleanField(default=False)
    staffUpdateDate = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.ippisNumber} - {{self.surname}} {{self.otherNames}}"

    def clean(self):
        super().clean()

        # Ensure LGA is in the same state as stateOfPosting
        if self.lgaOfOrigin and self.stateOfOrigin:
            if self.lgaOfOrigin.state != self.stateOfOrigin:
                raise ValidationError(
                    {'lgaOfOrigin': "LGA must be in the same state as stateOfPosting."})

        # Ensure grade level, cadre, and division combination exists in OfficialAppointment
        if self.gradeLevel and self.cadre and self.department:
            if not OfficialAppointment.objects.filter(
                gradeLevel=self.gradeLevel,
                cadre=self.cadre,
                department=self.department
            ).exists():
                raise ValidationError(
                    {
                        'gradeLevel': "This grade level, cadre, and department combination is not allowed."
                    }
                )

        # Ensure the division is in the same department
        if self.department and self.station:
            if self.station.state != self.stateOfPosting:
                raise ValidationError(
                    {'station': "Station must be in the same state as stateOfPosting."})

    def compareWithEmployee(self, employee):
        discrepancies = []
        fieldsToCompare = [
            ('dateOfBirth', 'DOB'),
            ('dateOfFirstAppointment', 'DOF'),
            ('dateOfPresentAppointment', 'DOP'),
            ('dateOfConfirmation', 'DOC'),
            ('department', 'DEPT'),
            ('stateOfPosting', 'SOP'),
        ]

        for field, discrepancyType in fieldsToCompare:
            auditValue = getattr(self, field)
            employeeValue = getattr(employee, field)

            if auditValue != employeeValue:
                discrepancies.append({
                    'type': discrepancyType,
                    'auditValue': str(auditValue),
                    'employeeValue': str(employeeValue)
                })

        return discrepancies

class StaffAuditEducation(models.Model):
    staff = models.ForeignKey(StaffAuditEmployee, on_delete=models.CASCADE)
    qualification = models.CharField(max_length=50)
    institution = models.CharField(max_length=50, null=True, blank=True)
    yearOfCertificateObtained = models.DateField(null=True, blank=True)
    monthOfCertificateObtained = models.DateField(null=True, blank=True)
    dayOfCertificateObtained = models.DateField(null=True, blank=True)
    CERTIFICATE_TYPES = [
        ('PSLC', 'Primary School Leaving Certificate'),
        ('JSCE', 'Junior Secondary School Certificate'),
        ('SSCE', 'Senior Secondary School Certificate'),
        ('OND', 'Ordinary National Diploma'),
        ('HND', 'Higher National Diploma'),
        ('BSC', 'Bachelor Degree'),
        ('PGD', 'Postgraduate Diploma'),
        ('MSC', 'Master Degree'),
        ('PHD', 'Doctorate Degree'),
        ('PROF', 'Professional Certification'),
    ]
    certifucateType = models.CharField(
        max_length=4, choices=CERTIFICATE_TYPES, null=True, blank=True)


class Employee(models.Model):
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female')]
    MARITAL_STATUS_CHOICES = [
        ('S', 'Single'),
        ('M', 'Married'),
        ('D', 'Divorced'),
        ('W', 'Widowed'),
    ]
    CADRE_CHOICES = [
        ('O', 'OFFICER'),
        ('E', 'EXECUTIVE'),
        ('S', 'SECRETARIAL'),
        ('C', 'CLERICAL'),
        ('D', 'DRIVER'),
    ]
    ACCOUNT_TYPES = [
        ('S', 'Savings'),
        ('C', 'Current'),
    ]

    # Personal Information
    ippisNumber = models.CharField(
        max_length=8, unique=True, verbose_name="IPPIS Number")
    fileNumber = models.CharField(
        max_length=7, unique=False, blank=True, null=True, verbose_name="File Number")
    nin = models.CharField(max_length=11, unique=True, blank=True,
                           null=True, verbose_name="National Identification Number")
    firstName = models.CharField(
        max_length=50, blank=True, verbose_name="First Name")
    lastName = models.CharField(
        max_length=50, blank=True, verbose_name="Surname")
    middleName = models.CharField(
        max_length=50, blank=True, verbose_name="Middle Name")
    dateOfBirth = models.DateField(
        null=True, blank=True, verbose_name="Date of Birth")
    gender = models.CharField(
        max_length=1, choices=GENDER_CHOICES, blank=True, verbose_name="Gender")
    maritalStatus = models.CharField(
        max_length=1, choices=MARITAL_STATUS_CHOICES, blank=True, verbose_name="Marital Status")
    phoneNumber = models.CharField(
        max_length=15, blank=True, verbose_name="Phone Number")
    emailAddress = models.EmailField(
        unique=True, blank=True, null=True, verbose_name="Email Address")
    residentialAddress =models.CharField(max_length=150,
        blank=True, verbose_name="Residential Address")
    stateOfOrigin = models.ForeignKey('State', on_delete=models.PROTECT,
                                      related_name='employeesOrigin', null=True, blank=True, verbose_name="State of Origin")
    lgaOfOrigin = models.ForeignKey('LGA', on_delete=models.PROTECT,
                                    related_name='employeesOrigin', null=True, blank=True, verbose_name="LGA of Origin")

    # Employment Information
    dateOfFirstAppointment = models.DateField(
        null=True, blank=True, verbose_name="Date of First Appointment")
    dateOfPresentAppointment = models.DateField(
        null=True, blank=True, verbose_name="Date of Present Appointment")
    dateOfConfirmation = models.DateField(
        null=True, blank=True, verbose_name="Date of Confirmation")
    cadre = models.CharField(max_length=1, choices=CADRE_CHOICES, null=True, blank=True, verbose_name="Cadre",
                             help_text="Select your cadre. Officers are those that have a BSC Degree and above. Executives are those that have Higher National Diploma and below")
    currentGradeLevel = models.ForeignKey(
        'GradeLevel', on_delete=models.PROTECT, null=True, blank=True, verbose_name="Current Grade Level")
    currentStep = models.PositiveIntegerField(
        null=True, blank=True, verbose_name="Current Step")
    department = models.ForeignKey(
        'Department', on_delete=models.PROTECT, null=True, blank=True, verbose_name="Department")
    division = models.ForeignKey(
        'Division', on_delete=models.PROTECT, null=True, blank=True, verbose_name="Division")
    passport = models.ImageField(
        upload_to='employee_passports/', null=True, blank=True, verbose_name="Passport Photo",
        help_text="Please Upload your passport photo here")
    stateOfPosting = models.ForeignKey('State', on_delete=models.PROTECT,
                                       related_name='employeesPosting', null=True, blank=True, verbose_name="State of Posting")
    station = models.ForeignKey(
        'LGA', on_delete=models.PROTECT, null=True, blank=True, related_name='employeesLgaPosting', verbose_name="Station")
    presentAppointment = models.ForeignKey('OfficialAppointment', on_delete=models.PROTECT, null=True,
                                           blank=True, verbose_name="Present Appointment", help_text="Select your Present Appointment")
    lastPromotionDate = models.DateField(
        null=True, blank=True, verbose_name="Last Promotion Date")
    retirementDate = models.DateField(
        null=True, blank=True, verbose_name="Retirement Date")
    isOnLeave = models.BooleanField(default=False, verbose_name="Is On Leave")
    isUnderDisciplinaryAction = models.BooleanField(
        default=False, verbose_name="Under Disciplinary Action")

    # Financial Details
    bank = models.ForeignKey(
        'Bank', on_delete=models.PROTECT, blank=True, null=True)
    accountType = models.CharField(
        max_length=1, choices=ACCOUNT_TYPES, blank=True, null=True)
    accountNumber = models.CharField(max_length=10, validators=[
                                     RegexValidator(r'^\d{10}$')], blank=True, null=True)
    pfa = models.ForeignKey(
        'PFA', on_delete=models.PROTECT, null=True, blank=True)
    pfaNumber = models.CharField(max_length=12, blank=True, validators=[
                                 RegexValidator(r'^\d{12}$')])

    # Spouse Details
    spouse_fullName = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Spouse Full Name")
    spouse_occupation = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Spouse Occupation")
    spouse_employerName = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Spouse Employer Name")
    spouse_employmentPeriod = models.CharField(
        max_length=50, blank=True, null=True, verbose_name="Spouse Employment Period")

    # Metadata
    createdAt = models.DateTimeField(
        auto_now_add=True, verbose_name="Created At")
    updatedAt = models.DateTimeField(auto_now=True, verbose_name="Updated At")
    updatedBy = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                  blank=True, related_name='employeeUpdates', verbose_name="Updated By")

    # Profile update flags
    isProfileUpdated = models.BooleanField(
        default=False, verbose_name="Profile Updated")
    profileUpdateDate = models.DateTimeField(
        null=True, blank=True, verbose_name="Profile Update Date")
    isPersonalInfoUpdated = models.BooleanField(default=False)
    isEmploymentInfoUpdated = models.BooleanField(default=False)
    isEducationInfoUpdated = models.BooleanField(default=False)
    financialInfoUpdated = models.BooleanField(default=False)
    isNextOfKinUpdated = models.BooleanField(default=False)
    isSpouseInfoUpdated = models.BooleanField(default=False)
    isPreviousEmploymentUpdated = models.BooleanField(default=False)
    
    # Approval fields
    isPassportApproved = models.BooleanField(default=False)
    isPersonalInfoApproved = models.BooleanField(default=False)
    isEmploymentInfoApproved = models.BooleanField(default=False)
    isEducationInfoApproved = models.BooleanField(default=False)
    isFinancialInfoApproved = models.BooleanField(default=False)
    isNextOfKinInfoApproved = models.BooleanField(default=False)
    isSpouseInfoApproved = models.BooleanField(default=False)
    isPreviousEmploymentApproved = models.BooleanField(default=False)


    # Vreification contorls
    isVerified = models.BooleanField(default=False)
    isFlagged = models.BooleanField(default=False)
    verifiedBy = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                   blank=True, related_name='employeeVerification', verbose_name="Verified By")
    verificationDate = models.DateTimeField(
        null=True, blank=True, verbose_name="Verification Date")
    verificationNotes = models.TextField(
        blank=True, verbose_name="Verification Notes")

    def __str__(self):
        return f"{self.firstName} {self.lastName} - {self.ippisNumber}"

    def clean(self):
        super().clean()

        # Check that date of first appointment is not in the future
        if self.dateOfFirstAppointment and self.dateOfFirstAppointment > date.today():
            raise ValidationError(
                {'dateOfFirstAppointment': 'Date of first appointment cannot be in the future.'})

        # Check that date of present appointment is not before date of first appointment
        if self.dateOfFirstAppointment and self.dateOfPresentAppointment and self.dateOfPresentAppointment < self.dateOfFirstAppointment:
            raise ValidationError(
                {'dateOfPresentAppointment': 'Date of present appointment cannot be before date of first appointment.'})

        # Check that date of confirmation is not before date of first appointment
        if self.dateOfFirstAppointment and self.dateOfConfirmation and self.dateOfConfirmation < self.dateOfFirstAppointment:
            raise ValidationError(
                {'dateOfConfirmation': 'Date of confirmation cannot be before date of first appointment.'})

        # Check that last promotion date is not before date of first appointment
        if self.dateOfFirstAppointment and self.lastPromotionDate and self.lastPromotionDate < self.dateOfFirstAppointment:
            raise ValidationError(
                {'lastPromotionDate': 'Last promotion date cannot be before date of first appointment.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        if not self.pk:
            self.profileUpdateDate = timezone.now()
        super().save(*args, **kwargs)

    def calculate_retirementDate(self):
        if not all([self.dateOfFirstAppointment, self.dateOfBirth, self.currentGradeLevel]):
            return None
        today = date.today()
        years_in_service = today.year - self.dateOfFirstAppointment.year
        if self.currentGradeLevel.name == 'Director General':
            retirementDate = self.dateOfBirth.replace(
                year=today.year + 65 - (today.year - self.dateOfBirth.year))
        elif years_in_service >= 35:
            retirementDate = self.dateOfFirstAppointment + \
                timedelta(days=365*35)
        else:
            age = today.year - self.dateOfBirth.year
            if age >= 60:
                retirementDate = self.dateOfBirth.replace(year=today.year)
            else:
                retirementDate = self.dateOfBirth.replace(
                    year=today.year + 60 - age)
        return retirementDate

    def calculate_retirementDate(self):
        if not self.isEmploymentInfoUpdated or not self.isPersonalInfoUpdated:
            return None

        if not all([self.dateOfFirstAppointment, self.dateOfBirth, self.currentGradeLevel]):
            return None

        today = date.today()
        years_in_service = today.year - self.dateOfFirstAppointment.year

        if years_in_service >= 35:
            retirementDate = self.dateOfFirstAppointment + timedelta(days=365*35)
        else:
            age = today.year - self.dateOfBirth.year
            if age >= 60:
                retirementDate = self.dateOfBirth.replace(year=today.year)
            else:
                retirementDate = self.dateOfBirth.replace(year=today.year + 60 - age)

        return retirementDate

    class Meta:
        ordering = ['lastName', 'firstName']
        verbose_name = "Employee"
        verbose_name_plural = "Employees"


class EducationAndTraining(models.Model):
    ACTIVITY_TYPE_CHOICES = [
        ('FE', 'Formal Education'),
        ('PC', 'Professional Certification'),
        ('SC', 'Short Course'),
        ('WT', 'Workshop/Training'),
        ('CO', 'Conference'),
        ('OT', 'Other'),
    ]
    LEVEL_CHOICES = [
        ('PSLC', 'Primary School Leaving Certificate'),
        ('JSCE', 'Junior Secondary School Certificate'),
        ('SSCE', 'Senior Secondary School Certificate'),
        ('OND', 'Ordinary National Diploma'),
        ('HND', 'Higher National Diploma'),
        ('BSC', 'Bachelor Degree'),
        ('PGD', 'Postgraduate Diploma'),
        ('MSC', 'Master Degree'),
        ('PHD', 'Doctorate Degree'),
        ('PROF', 'Professional Certification'),
        ('NA', 'Not Applicable'),
    ]
    MODE_OF_STUDY_CHOICES = [
        ('FT', 'Full Time'),
        ('PT', 'Part Time'),
        ('DL', 'Distance Learning'),
        ('OL', 'Online'),
        ('NA', 'Not Applicable'),
    ]

    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name='educationAndTraining')
    activityType = models.CharField(
        max_length=2, choices=ACTIVITY_TYPE_CHOICES)
    title = models.CharField(
        max_length=50, help_text="Title of the degree, certification, or course, \n(e.g. Primary School Ceritificate, SSCE, WAEC, GCE, BSC, BA, B.Ed")
    fieldOfStudy = models.CharField(max_length=50,blank=True, null=True, verbose_name='Field of Study')
    institution = models.CharField(max_length=255)
    level = models.CharField(
        max_length=4, choices=LEVEL_CHOICES, verbose_name="Level of Education")
    startDate = models.DateField(verbose_name="Start Date of Program")
    endDate = models.DateField(
        null=True, blank=True, help_text="End date of Program. Leave blank if ongoing")
    certificateObtained = models.BooleanField(default=False, verbose_name="Certificate Obtained?",
                                              help_text="Tick if certificate obtained")
    isVerified = models.BooleanField(default=False)
    verifiedBy = models.ForeignKey(User, on_delete=models.SET_NULL,
                                   null=True, blank=True, related_name='educationVerifications')
    verificationDate = models.DateField(null=True, blank=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.employee.firstName} {self.employee.lastName} - {self.title}"

    class Meta:
        ordering = ['-endDate', '-startDate']
        verbose_name = "Education and Training Record"
        verbose_name_plural = "Education and Training Records"


class PreviousEmployment(models.Model):
    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name='previousEmployments')
    employer = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="Employer Name")
    organisation = models.CharField(
        max_length=255, verbose_name="Organisation Name")
    position = models.CharField(max_length=255, verbose_name="Position Title")
    startDate = models.DateField()
    endDate = models.DateField()
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def clean(self):
        super().clean()
        if self.startDate >= self.endDate:
            raise ValidationError('End date must be after start date.')
        if self.endDate > date.today():
            raise ValidationError('End date cannot be in the future.')

    def __str__(self):
        return f"{self.employee.firstName} {self.employee.lastName} - {self.employer}"

    class Meta:
        ordering = ['-endDate', '-startDate']
        verbose_name = "Previous Employment"
        verbose_name_plural = "Previous Employments"



class NextOfKin(models.Model):
    RELATIONSHIP_CHOICES = [
        ('SPOUSE', 'Spouse'),
        ('CHILD', 'Child'),
        ('PARENT', 'Parent'),
        ('SIBLING', 'Sibling'),
        ('OTHER', 'Other'),
    ]
    employee = models.OneToOneField(
        Employee, on_delete=models.CASCADE, related_name='nextOfKin'
    )
    # Next of Kin 1
    nok1_fullName = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Next of Kin 1 Full Name")
    nok1_relationship = models.CharField(
        max_length=20, choices=RELATIONSHIP_CHOICES, blank=True, null=True, verbose_name="Next of Kin 1 Relationship")
    nok1_address = models.CharField(max_length=150,
        blank=True, null=True, verbose_name="Next of Kin 1 Address")
    nok1_phoneNumber = models.CharField(max_length=11, validators=[RegexValidator(
        r'^(080|081|090|091|070)\d{8}$')], blank=True, null=True, verbose_name="Next of Kin 1 Phone Number")

    # Next of Kin 2
    nok2_fullName = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Next of Kin 2 Full Name")
    nok2_relationship = models.CharField(
        max_length=20, choices=RELATIONSHIP_CHOICES, blank=True, null=True, verbose_name="Next of Kin 2 Relationship")
    nok2_address =models.CharField(max_length=150,
        blank=True, null=True, verbose_name="Next of Kin 2 Address")
    nok2_phoneNumber = models.CharField(max_length=11, validators=[RegexValidator(
        r'^(080|081|090|091|070)\d{8}$')], blank=True, null=True, verbose_name="Next of Kin 2 Phone Number")

    def __str__(self):
        return f"{self.employee.firstName} {self.employee.lastName} - Next of Kin"

    class Meta:
        verbose_name = "Next of Kin"
        verbose_name_plural = "Next of Kin"
        

class Ticket(models.Model):
    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('URGENT', 'Urgent'),
    ]

    subject = models.CharField(max_length=200)
    description = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tickets')
    created_at = models.DateTimeField(auto_now_add=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='MEDIUM')
    is_resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_tickets')
    resolved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Ticket #{self.id}: {self.subject}"

    class Meta:
        ordering = ['-created_at']
        
        
class CustomReport(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    model_name = models.CharField(max_length=50)
    fields = models.JSONField()
    filters = models.JSONField(default=dict)
    order_by = models.CharField(max_length=50, blank=True)
    
    def __str__(self):
        return self.name

class ReportSchedule(models.Model):
    report = models.ForeignKey(CustomReport, on_delete=models.CASCADE)
    frequency = models.CharField(max_length=20, choices=[
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly')
    ])
    recipients = models.ManyToManyField(User, related_name='scheduled_reports')
    last_run = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.report.name} - {self.get_frequency_display()}"
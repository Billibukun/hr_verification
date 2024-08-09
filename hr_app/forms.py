import base64
from io import BytesIO
from django.forms import inlineformset_factory
from .models import Discrepancy, Employee, EducationAndTraining, PreviousEmployment
from crispy_tailwind.layout import Button
from crispy_forms.layout import Layout, Submit, Row, Column
from crispy_forms.helper import FormHelper
from django.contrib.auth.forms import AuthenticationForm
from django import forms
from .models import *
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, Div, Field
from crispy_tailwind.layout import *
from django.core.exceptions import ValidationError
from crispy_forms.helper import FormHelper
from crispy_tailwind.layout import Button
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from PIL import Image
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile

class UserCreateForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    is_staff = forms.BooleanField(required=False, label="Staff Status")
    is_active = forms.BooleanField(required=False, initial=True, label="Active")

    # UserProfile fields
    role = forms.ChoiceField(choices=UserProfile.USER_ROLES, required=True)
    phoneNumber = forms.CharField(max_length=11, required=False)
    ippisNumber = forms.CharField(max_length=8, required=False)
    department = forms.ModelChoiceField(queryset=Department.objects.all(), required=False)
    stateOfPosting = forms.ModelChoiceField(queryset=State.objects.all(), required=False)
    allowedStates = forms.ModelMultipleChoiceField(queryset=State.objects.all(), required=False)
    allowedDepartments = forms.ModelMultipleChoiceField(queryset=Department.objects.all(), required=False)
    allowedZones = forms.ModelMultipleChoiceField(queryset=Zone.objects.all(), required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2', 'is_staff', 'is_active']

    def clean_ippisNumber(self):
        ippisNumber = self.cleaned_data.get('ippisNumber')
        if ippisNumber and UserProfile.objects.filter(ippisNumber=ippisNumber).exists():
            raise ValidationError("This IPPIS number is already in use.")
        return ippisNumber

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.is_staff = self.cleaned_data['is_staff']
        user.is_active = self.cleaned_data['is_active']
        
        if commit:
            user.save()
            user_profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'role': self.cleaned_data['role'],
                    'phoneNumber': self.cleaned_data['phoneNumber'],
                    'ippisNumber': self.cleaned_data['ippisNumber'],
                    'department': self.cleaned_data['department'],
                    'stateOfPosting': self.cleaned_data['stateOfPosting']
                }
            )
            if not created:
                user_profile.role = self.cleaned_data['role']
                user_profile.phoneNumber = self.cleaned_data['phoneNumber']
                user_profile.ippisNumber = self.cleaned_data['ippisNumber']
                user_profile.department = self.cleaned_data['department']
                user_profile.stateOfPosting = self.cleaned_data['stateOfPosting']
                user_profile.save()
            
            user_profile.allowedStates.set(self.cleaned_data['allowedStates'])
            user_profile.allowedDepartments.set(self.cleaned_data['allowedDepartments'])
            user_profile.allowedZones.set(self.cleaned_data['allowedZones'])
        
        return user
    

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    is_staff = forms.BooleanField(required=False, label="Staff Status")
    is_active = forms.BooleanField(required=False, initial=True, label="Active")

    # UserProfile fields
    role = forms.ChoiceField(choices=UserProfile.USER_ROLES, required=True)
    phoneNumber = forms.CharField(max_length=11, required=False)
    ippisNumber = forms.CharField(max_length=8, required=False)
    department = forms.ModelChoiceField(queryset=Department.objects.all(), required=False)
    stateOfPosting = forms.ModelChoiceField(queryset=State.objects.all(), required=False)
    allowedStates = forms.ModelMultipleChoiceField(queryset=State.objects.all(), required=False)
    allowedDepartments = forms.ModelMultipleChoiceField(queryset=Department.objects.all(), required=False)
    allowedZones = forms.ModelMultipleChoiceField(queryset=Zone.objects.all(), required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'department',]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['role'].initial = self.instance.userprofile.role
            self.fields['phoneNumber'].initial = self.instance.userprofile.phoneNumber
            self.fields['ippisNumber'].initial = self.instance.userprofile.ippisNumber
            self.fields['department'].initial = self.instance.userprofile.department
            self.fields['stateOfPosting'].initial = self.instance.userprofile.stateOfPosting
            self.fields['allowedStates'].initial = self.instance.userprofile.allowedStates.all()
            self.fields['allowedDepartments'].initial = self.instance.userprofile.allowedDepartments.all()
            self.fields['allowedZones'].initial = self.instance.userprofile.allowedZones.all()

    def clean_ippisNumber(self):
        ippisNumber = self.cleaned_data.get('ippisNumber')
        if ippisNumber and ippisNumber != self.instance.userprofile.ippisNumber:
            if UserProfile.objects.filter(ippisNumber=ippisNumber).exists():
                raise ValidationError("This IPPIS number is already in use.")
        return ippisNumber

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            user_profile = self.instance.userprofile
            user_profile.role = self.cleaned_data['role']
            user_profile.phoneNumber = self.cleaned_data['phoneNumber']
            user_profile.ippisNumber = self.cleaned_data['ippisNumber']
            user_profile.department = self.cleaned_data['department']
            user_profile.stateOfPosting = self.cleaned_data['stateOfPosting']
            user_profile.save()
            user_profile.allowedStates.set(self.cleaned_data['allowedStates'])
            user_profile.allowedDepartments.set(self.cleaned_data['allowedDepartments'])
            user_profile.allowedZones.set(self.cleaned_data['allowedZones'])
        return user

class AdminLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-primary focus:border-primary focus:z-10 sm:text-sm', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-primary focus:border-primary focus:z-10 sm:text-sm', 'placeholder': 'Password'}))


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['role', 'phoneNumber', 'department', 'stateOfPosting',
                  'allowedStates', 'allowedDepartments', 'allowedZones']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Get available states for 'allowedStates' field
        self.fields['allowedStates'].queryset = State.objects.all()

        # Get available departments for 'allowedDepartments' field
        self.fields['allowedDepartments'].queryset = Department.objects.all()

        # Get available zones for 'allowedZones' field
        self.fields['allowedZones'].queryset = Zone.objects.all()

        # Set the initial values for 'allowedStates' and 'allowedDepartments' fields based on the current user's department and state
        if self.instance.pk:  # If the UserProfile is being edited
            current_user = self.instance.user
            if current_user.userprofile.role in ['HR_ADMIN', 'DRUDID_VIEWER','IT_ADMIN', 'SUPER_ADMIN']:
                self.fields['allowedStates'].initial = State.objects.all()  # Allow selection of all states for HR_ADMIN
                self.fields['allowedDepartments'].initial = Department.objects.all()  # Allow selection of all departments for HR_ADMIN
            else:
                # Set initial 'allowedStates' and 'allowedDepartments' based on current user's data
                self.fields['allowedStates'].initial = current_user.userprofile.allowedStates.all()
                self.fields['allowedDepartments'].initial = current_user.userprofile.allowedDepartments.all()

        #  Display 'allowedStates' and 'allowedDepartments' as read-only fields unless the user is an HR_ADMIN
        if self.instance.user.userprofile.role not in ['HR_ADMIN', 'DRUDID_VIEWER','IT_ADMIN', 'SUPER_ADMIN']:
            self.fields['allowedStates'].widget = forms.SelectMultiple(attrs={'disabled': True})
            self.fields['allowedDepartments'].widget = forms.SelectMultiple(attrs={'disabled': True})
            self.fields['allowedZones'].widget = forms.SelectMultiple(attrs={'disabled': True})  # Also display allowed zones as read-only

        

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name',
                  'last_name', 'is_staff', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customize widgets for fields you want to modify
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        self.fields['first_name'].widget.attrs.update(
            {'class': 'form-control'})
        self.fields['last_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['is_staff'].widget.attrs.update(
            {'class': 'form-check-input'})
        self.fields['is_active'].widget.attrs.update(
            {'class': 'form-check-input'})

        # Add a placeholder for the username field
        self.fields['username'].widget.attrs.update(
            {'placeholder': 'Username'})

        # Change the label for the email field
        self.fields['email'].label = 'Email Address'

        # Set initial values for is_staff and is_active
        if 'instance' in kwargs and kwargs['instance'].pk:
            self.fields['is_staff'].initial = kwargs['instance'].is_staff
            self.fields['is_active'].initial = kwargs['instance'].is_active
        else:
            # Set initial values for new users (adjust as needed)
            self.fields['is_staff'].initial = False
            self.fields['is_active'].initial = True


class StateForm(forms.ModelForm):
    class Meta:
        model = State
        fields = ['name']


class LGAForm(forms.ModelForm):
    class Meta:
        model = LGA
        fields = ['name', 'state']


class DivisionForm(forms.ModelForm):
    class Meta:
        model = Division
        fields = ['code', 'name', 'department']


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['code', 'name']


class GradeLevelForm(forms.ModelForm):
    class Meta:
        model = GradeLevel
        fields = ['level', 'name', 'description', 'perDiem',
                  'localRunning', 'estacode', 'assumptionOfDuty']


class OfficialAppointmentForm(forms.ModelForm):
    class Meta:
        model = OfficialAppointment
        fields = ['code', 'name', 'gradeLevel', 'cadre', 'department']



class UserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'space-y-6'
        self.helper.layout = Layout(
            'username',
            'password',
            Button('submit', 'Log in', css_class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500")
        )


class EmployeeLoginForm(forms.Form):
    ippis_number = forms.CharField(max_length=8, required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'space-y-6'
        self.helper.layout = Layout(
            'ippis_number',
            Button('submit', 'Login', css_class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500")
        )

class DateInput(forms.DateInput):
    input_type = 'date'

class PersonalInfoForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['fileNumber', 'nin', 'firstName', 'lastName', 'middleName', 'passport', 'dateOfBirth', 'gender', 
                  'maritalStatus', 'phoneNumber', 'emailAddress', 'residentialAddress', 'stateOfOrigin', 'lgaOfOrigin']
        widgets = {
            'dateOfBirth': DateInput(),
            'passport': forms.FileInput(attrs={'accept': 'image/*'}),
        }
        
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields['dateOfBirth'].disabled = True
    #     self.fields['fileNumber'].disabled = True

    def clean_passport(self):
        passport = self.cleaned_data.get('passport')
        if passport:
            try:
                # Open the uploaded image
                img = Image.open(passport)
                
                # Convert to RGB if it's not already
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Resize the image (adjust the size as needed)
                img.thumbnail((300, 300))  # Adjust the thumbnail size
                
                # Save the image to a BytesIO object
                output = BytesIO()
                img.save(output, format='JPEG', quality=85)
                output.seek(0)
                
                # Create a new ContentFile from the BytesIO
                content_file = ContentFile(output.read())
                
                # Create a new file name
                name = f"passport_{self.instance.ippisNumber}.jpg"
                
                # Return the new image file
                return InMemoryUploadedFile(content_file, None, name, 'image/jpeg', content_file.tell, None)
            except Exception as e:
                raise forms.ValidationError(f"Error processing image: {str(e)}")
        return passport

    def save(self, commit=True):
        instance = super().save(commit=False)
        passport = self.cleaned_data.get('passport')
        if passport:
            instance.passport = passport
        if commit:
            instance.save()
        return instance
    

class EmploymentInfoForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['fileNumber','dateOfFirstAppointment', 'dateOfPresentAppointment', 'dateOfConfirmation',
                  'cadre', 'currentGradeLevel', 'currentStep', 'stateOfPosting','station',
                  'department', 'division', 'presentAppointment', 'lastPromotionDate']
        widgets = {
            'dateOfFirstAppointment': DateInput(),
            'dateOfPresentAppointment': DateInput(),
            'dateOfConfirmation': DateInput(),
            'lastPromotionDate': DateInput(),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  # Correctly calling super() with the form class
        self.fields['fileNumber'].disabled = True 
        
class EducationAndTrainingForm(forms.ModelForm):
    class Meta:
        model = EducationAndTraining
        exclude = ['id','employee', 'isVerified', 'verifiedBy', 'verificationDate', 'createdAt', 'updatedAt']
        widgets = {
            'startDate': DateInput(),
            'endDate': DateInput(),
        }

EducationFormSet = inlineformset_factory(
    Employee, EducationAndTraining, 
    form=EducationAndTrainingForm, 
    extra=1, max_num=10
)

class PreviousEmploymentForm(forms.ModelForm):
    class Meta:
        model = PreviousEmployment
        exclude = ['id','employee', 'createdAt', 'updatedAt']
        widgets = {
            'startDate': DateInput(),
            'endDate': DateInput(),
        }

PreviousEmploymentFormSet = inlineformset_factory(
    Employee, PreviousEmployment, 
    form=PreviousEmploymentForm, 
    extra=1,
)

class NextOfKinForm(forms.ModelForm):
    class Meta:
        model = NextOfKin
        exclude = ['id','employee']

class FinancialInfoForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['bank', 'accountType', 'accountNumber', 'pfa', 'pfaNumber']

class SpouseInfoForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['spouse_fullName', 'spouse_occupation', 'spouse_employerName', 'spouse_employmentPeriod']


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            'ippisNumber', 'fileNumber', 'firstName', 'lastName', 'middleName',
            'dateOfBirth', 'gender', 'maritalStatus', 'phoneNumber', 'emailAddress',
            'residentialAddress', 'stateOfOrigin', 'lgaOfOrigin',
            'dateOfFirstAppointment', 'dateOfPresentAppointment', 'dateOfConfirmation',
            'cadre', 'currentGradeLevel', 'currentStep', 'department', 'stateOfPosting',
            'presentAppointment', 'lastPromotionDate', 'retirementDate',
            'bank', 'accountType', 'accountNumber', 'pfa', 'pfaNumber',
            'spouse_fullName', 'spouse_occupation', 'spouse_employerName', 'spouse_employmentPeriod',
            'passport'
        ]
        widgets = {
            'dateOfBirth': forms.DateInput(attrs={'type': 'date'}),
            'dateOfFirstAppointment': forms.DateInput(attrs={'type': 'date'}),
            'dateOfPresentAppointment': forms.DateInput(attrs={'type': 'date'}),
            'dateOfConfirmation': forms.DateInput(attrs={'type': 'date'}),
            'lastPromotionDate': forms.DateInput(attrs={'type': 'date'}),
            'retirementDate': forms.DateInput(attrs={'type': 'date'}),
            'gender': forms.RadioSelect,
            'maritalStatus': forms.RadioSelect,
            'cadre': forms.RadioSelect,
            'accountType': forms.RadioSelect,
        }

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.helper = FormHelper()
    #     self.helper.form_tag = True
    #     self.helper.form_class = 'space-y-6'
    #     self.helper.layout = Layout(
    #         Fieldset(
    #             'Personal Information',
    #             Div(
    #                 Div('ippisNumber', css_class='w-full md:w-1/3 px-3 mb-6 md:mb-0'),
    #                 Div('fileNumber', css_class='w-full md:w-1/3 px-3 mb-6 md:mb-0'),
    #                 Div('passport', css_class='w-full md:w-1/3 px-3 mb-6 md:mb-0'),
    #                 css_class='flex flex-wrap -mx-3 mb-6'
    #             ),
    #             Div(
    #                 Div('firstName', css_class='w-full md:w-1/3 px-3 mb-6 md:mb-0'),
    #                 Div('lastName', css_class='w-full md:w-1/3 px-3 mb-6 md:mb-0'),
    #                 Div('middleName', css_class='w-full md:w-1/3 px-3 mb-6 md:mb-0'),
    #                 css_class='flex flex-wrap -mx-3 mb-6'
    #             ),
    #             Div(
    #                 Div('dateOfBirth', css_class='w-full md:w-1/3 px-3 mb-6 md:mb-0'),
    #                 Div('gender', css_class='w-full md:w-1/3 px-3 mb-6 md:mb-0'),
    #                 Div('maritalStatus', css_class='w-full md:w-1/3 px-3 mb-6 md:mb-0'),
    #                 css_class='flex flex-wrap -mx-3 mb-6'
    #             ),
    #             'phoneNumber',
    #             'emailAddress',
    #             'residentialAddress',
    #             Div(
    #                 Div('stateOfOrigin', css_class='w-full md:w-1/2 px-3 mb-6 md:mb-0'),
    #                 Div('lgaOfOrigin', css_class='w-full md:w-1/2 px-3 mb-6 md:mb-0'),
    #                 css_class='flex flex-wrap -mx-3 mb-6'
    #             ),
    #         ),
    #         Fieldset(
    #             'Employment Information',
    #             Div(
    #                 Div('dateOfFirstAppointment', css_class='w-full md:w-1/3 px-3 mb-6 md:mb-0'),
    #                 Div('dateOfPresentAppointment', css_class='w-full md:w-1/3 px-3 mb-6 md:mb-0'),
    #                 Div('dateOfConfirmation', css_class='w-full md:w-1/3 px-3 mb-6 md:mb-0'),
    #                 css_class='flex flex-wrap -mx-3 mb-6'
    #             ),
    #             Div(
    #                 Div('cadre', css_class='w-full md:w-1/3 px-3 mb-6 md:mb-0'),
    #                 Div('currentGradeLevel', css_class='w-full md:w-1/3 px-3 mb-6 md:mb-0'),
    #                 Div('currentStep', css_class='w-full md:w-1/3 px-3 mb-6 md:mb-0'),
    #                 css_class='flex flex-wrap -mx-3 mb-6'
    #             ),
    #             Div(
    #                 Div('department', css_class='w-full md:w-1/2 px-3 mb-6 md:mb-0'),
    #                 Div('stateOfPosting', css_class='w-full md:w-1/2 px-3 mb-6 md:mb-0'),
    #                 css_class='flex flex-wrap -mx-3 mb-6'
    #             ),
    #             'presentAppointment',
    #             Div(
    #                 Div('lastPromotionDate', css_class='w-full md:w-1/2 px-3 mb-6 md:mb-0'),
    #                 Div('retirementDate', css_class='w-full md:w-1/2 px-3 mb-6 md:mb-0'),
    #                 css_class='flex flex-wrap -mx-3 mb-6'
    #             ),
    #         ),
    #         Fieldset(
    #             'Financial Information',
    #             Div(
    #                 Div('bank', css_class='w-full md:w-1/2 px-3 mb-6 md:mb-0'),
    #                 Div('accountType', css_class='w-full md:w-1/2 px-3 mb-6 md:mb-0'),
    #                 css_class='flex flex-wrap -mx-3 mb-6'
    #             ),
    #             'accountNumber',
    #             Div(
    #                 Div('pfa', css_class='w-full md:w-1/2 px-3 mb-6 md:mb-0'),
    #                 Div('pfaNumber', css_class='w-full md:w-1/2 px-3 mb-6 md:mb-0'),
    #                 css_class='flex flex-wrap -mx-3 mb-6'
    #             ),
    #         ),
    #         Fieldset(
    #             'Spouse Information',
    #             'spouse_fullName',
    #             'spouse_occupation',
    #             'spouse_employerName',
    #             'spouse_employmentPeriod',
    #         ),
    #         ButtonHolder(
    #             Button('submit', 'Save', css_class='bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded')
    #         )
    #     )

    def clean(self):
        cleaned_data = super().clean()
        date_of_birth = cleaned_data.get('dateOfBirth')
        date_of_first_appointment = cleaned_data.get('dateOfFirstAppointment')
        date_of_present_appointment = cleaned_data.get('dateOfPresentAppointment')
        date_of_confirmation = cleaned_data.get('dateOfConfirmation')

        if date_of_birth and date_of_first_appointment:
            if date_of_first_appointment <= date_of_birth:
                raise ValidationError("Date of first appointment must be after date of birth.")

        if date_of_first_appointment and date_of_present_appointment:
            if date_of_present_appointment < date_of_first_appointment:
                raise ValidationError("Date of present appointment cannot be before date of first appointment.")

        if date_of_first_appointment and date_of_confirmation:
            if date_of_confirmation < date_of_first_appointment:
                raise ValidationError("Date of confirmation cannot be before date of first appointment.")

        return cleaned_data
    
class DiscrepancyResolveForm(forms.ModelForm):
    class Meta:
        model = Discrepancy
        fields = ['employeeValue', 'description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('employeeValue', css_class='form-group col-md-6 mb-0'),
                Column('description', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Submit('submit', 'Resolve Discrepancy', css_class='btn btn-primary')
        )


class EmployeeSearchForm(forms.Form):
    query = forms.CharField(required=False, label='Search')

class EmployeeFileNumberForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['fileNumber']

class DiscrepancyResolveForm(forms.ModelForm):
    class Meta:
        model = Discrepancy
        fields = ['resolution']

class CustomReportForm(forms.Form):
    MODEL_CHOICES = [
        ('Employee', 'Employee'),
        ('StaffAuditEmployee', 'Staff Audit Employee'),
        ('Discrepancy', 'Discrepancy'),
    ]
    
    model = forms.ChoiceField(choices=MODEL_CHOICES)
    fields = forms.MultipleChoiceField(choices=[], widget=forms.CheckboxSelectMultiple)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fields'].choices = self.get_model_fields()

    def get_model_fields(self):
        model_name = self.data.get('model') or self.initial.get('model')
        if model_name == 'Employee':
            return [(f.name, f.name) for f in Employee._meta.get_fields()]
        elif model_name == 'StaffAuditEmployee':
            return [(f.name, f.name) for f in StaffAuditEmployee._meta.get_fields()]
        elif model_name == 'Discrepancy':
            return [(f.name, f.name) for f in Discrepancy._meta.get_fields()]
        return []

class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['subject', 'description', 'priority']
        

from django import forms
from .models import CustomReport
from django.apps import apps
from django.core.exceptions import ValidationError
from django.db.models.fields.reverse_related import ForeignObjectRel


class CustomReportForm(forms.ModelForm):
    MODEL_CHOICES = [
        ('Employee', 'Employee'),
        ('Discrepancy', 'Discrepancy'),
        ('StaffAuditEmployee', 'Staff Audit Employee'),
    ]
    
    model_name = forms.ChoiceField(
        choices=MODEL_CHOICES, 
        widget=forms.Select(attrs={'class': 'form-select block w-full mt-1'})
    )
    fields = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-multiselect mt-1 block w-full'})
    )
    order_by = forms.ChoiceField(
        required=False,
        choices=[('', '---------')],
        widget=forms.Select(attrs={'class': 'form-select block w-full mt-1'})
    )
    items_per_page = forms.ChoiceField(
        choices=[(10, '10'), (25, '25'), (50, '50'), (100, '100')], 
        initial=25,
        widget=forms.Select(attrs={'class': 'form-select block w-full mt-1'})
    )
    
    class Meta:
        model = CustomReport
        fields = ['name', 'description', 'model_name', 'fields', 'order_by', 'items_per_page']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input block w-full mt-1'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea block w-full mt-1', 'rows': 3}),
        }
        
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fields'].choices = []
        
        if self.is_bound and 'model_name' in self.data:
            try:
                model_name = self.data.get('model_name')
                self.fields['fields'].choices = self.get_model_fields(model_name)
                self.fields['order_by'].choices += self.get_model_fields(model_name)
            except (KeyError, ValueError):
                pass
        elif self.instance.pk:
            self.fields['fields'].choices = self.get_model_fields(self.instance.model_name)
            self.fields['order_by'].choices += self.get_model_fields(self.instance.model_name)
    
    def get_model_fields(self, model_name):
        model = apps.get_model('hr_app', model_name)
        fields = []
        for f in model._meta.get_fields():
            if not f.is_relation:
                fields.append((f.name, f.verbose_name))
            elif isinstance(f, ForeignObjectRel):
                related_model = f.related_model
                for rf in related_model._meta.get_fields():
                    if not rf.is_relation:
                        fields.append((f'{f.name}__{rf.name}', f'{f.name.capitalize()} - {rf.verbose_name}'))
            elif f.is_relation:
                fields.append((f.name, f.verbose_name))
        return fields
        
    
class ReportFilterForm(forms.Form):
    field = forms.ChoiceField()
    operator = forms.ChoiceField(choices=[
        ('exact', 'Equals'),
        ('icontains', 'Contains'),
        ('gt', 'Greater Than'),
        ('lt', 'Less Than'),
        ('gte', 'Greater Than or Equal'),
        ('lte', 'Less Than or Equal'),
    ])
    value = forms.CharField()

    def __init__(self, *args, **kwargs):
        model_fields = kwargs.pop('model_fields', [])
        super().__init__(*args, **kwargs)
        self.fields['field'].choices = model_fields
        
        
class EmployeeDetailForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['firstName', 'lastName', 'ippisNumber', 'fileNumber', 'dateOfBirth', 'gender', 'maritalStatus', 
                  'phoneNumber', 'emailAddress', 'residentialAddress', 'stateOfOrigin', 'lgaOfOrigin', 
                  'dateOfFirstAppointment', 'dateOfPresentAppointment', 'dateOfConfirmation', 'cadre', 
                  'currentGradeLevel', 'currentStep', 'department', 'division', 'stateOfPosting', 'station', 
                  'presentAppointment', 'lastPromotionDate', 'bank', 'accountType', 'accountNumber', 'pfa', 'pfaNumber']

class EmployeeVerificationForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['verificationNotes']

class DiscrepancyResolutionForm(forms.ModelForm):
    class Meta:
        model = Discrepancy
        fields = ['isResolved', 'resolution']

class SectionApprovalForm(forms.Form):
    SECTIONS = [
        ('passport', 'Passport'),
        ('personal_info', 'Personal Information'),
        ('employment_info', 'Employment Information'),
        ('education_info', 'Education Information'),
        ('financial_info', 'Financial Information'),
        ('next_of_kin_info', 'Next of Kin Information'),
        ('spouse_info', 'Spouse Information'),
        ('previous_employment', 'Previous Employment'),
    ]
    section = forms.ChoiceField(choices=SECTIONS)
    is_approved = forms.BooleanField(required=False)
    


class DiscrepancyForm(forms.ModelForm):
    class Meta:
        model = Discrepancy
        fields = ['employeeValue', 'resolution']
        widgets = {
            'resolution': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['employeeValue'].label = "New Value"
        self.fields['resolutionComments'].label = "Resolution Comments"
        
        
class ResolveDiscrepancyForm(forms.ModelForm):
    employee_value = forms.CharField(label="Employee Value", required=False)
    resolution_comment = forms.CharField(widget=forms.Textarea, label="Resolution Comment", required=True)

    class Meta:
        model = Discrepancy
        fields = ['employee_value', 'resolution_comment']

    def __init__(self, *args, **kwargs):
        self.employee = kwargs.pop('employee', None)
        self.discrepancy = kwargs.pop('discrepancy', None)
        super().__init__(*args, **kwargs)
        if self.employee and self.discrepancy:
            field_name = self.discrepancy.discrepancyType.lower()
            self.fields['employee_value'].initial = getattr(self.employee, field_name)

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.employee and self.discrepancy:
            field_name = self.discrepancy.discrepancyType.lower()
            setattr(self.employee, field_name, self.cleaned_data['employee_value'])
            self.employee.save()
        if commit:
            instance.save()
        return instance
    
    
class FileNumberUpdateForm(forms.ModelForm):
    class Meta:
        model = StaffAuditEmployee  # We'll use this for both models since they share the fileNumber field
        fields = ['fileNumber']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fileNumber'].widget.attrs.update({'class': 'focus:ring-primary focus:border-primary block w-full sm:text-sm border-gray-300 rounded-md'})
        
        
from django import forms
from .models import Employee, Discrepancy

class FieldUpdateForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        super().__init__(*args, **kwargs)
        if fields:
            allowed = set(fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)

class DiscrepancyResolutionForm(forms.ModelForm):
    class Meta:
        model = Discrepancy
        fields = ['resolution']
        widgets = {
            'resolution': forms.Textarea(attrs={'rows': 3}),
        }

from django import forms
from .models import State

class FinalVerificationForm(forms.Form):
    verification_notes = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        required=False,
        label="Verification Notes"
    )
    
    # Change of Name fields
    change_of_name = forms.BooleanField(
        required=False,
        label="Request Change of Name"
    )
    new_last_name = forms.CharField(
        max_length=50,
        required=False,
        label="New Last Name"
    )
    new_first_name = forms.CharField(
        max_length=50,
        required=False,
        label="New First Name"
    )
    new_middle_name = forms.CharField(
        max_length=50,
        required=False,
        label="New Middle Name"
    )
    
    # Transfer Staff fields
    transfer_staff = forms.BooleanField(
        required=False,
        label="Transfer Staff"
    )
    transfer_to_state = forms.ModelChoiceField(
        queryset=State.objects.all(),
        required=False,
        label="Transfer to State"
    )
    
    # Image capture field (hidden field, will be populated via JavaScript)
    captured_image = forms.CharField(
        widget=forms.HiddenInput(),
        required=False
    )

    def clean(self):
        cleaned_data = super().clean()
        change_of_name = cleaned_data.get('change_of_name')
        transfer_staff = cleaned_data.get('transfer_staff')
        
        if change_of_name:
            if not cleaned_data.get('new_last_name'):
                self.add_error('new_last_name', 'New last name is required when requesting a name change.')
            if not cleaned_data.get('new_first_name'):
                self.add_error('new_first_name', 'New first name is required when requesting a name change.')
        
        if transfer_staff and not cleaned_data.get('transfer_to_state'):
            self.add_error('transfer_to_state', 'Transfer to state is required when transferring staff.')
        
        return cleaned_data
    
    
from django import forms
from .models import Employee, State, LGA, Department, GradeLevel

            
class StaffSearchForm(forms.Form):
    search_term = forms.CharField(max_length=100, label="Search by IPPIS or File Number")


class EmployeeVerificationForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            'ippisNumber', 'fileNumber', 'lastName','middleName', 'firstName', 'surname_ippis', 'middleName_ippis',
            'firstName_ippis', 'dateOfBirth', 'dateOfBirth_ippis',
            'gender', 'maritalStatus', 'phoneNumber', 'emailAddress',
            'residentialAddress', 'stateOfOrigin', 'lgaOfOrigin',
            'dateOfFirstAppointment', 'dateOfFirstAppointment_ippis', 'dateOfPresentAppointment', 'dateOfConfirmation',
             'lastPromotionDate',
            'stateOfPosting', 'station',
            'department', 'division', 'cadre', 'currentGradeLevel', 'currentStep', 'presentAppointment',
            'bank', 'accountType', 'accountNumber',
            'pfa','pfaNumber',
            'nok1_name', 'nok1_relationship', 'nok1_phoneNumber', 'nok1_address',
            'nok2_name', 'nok2_relationship', 'nok2_phoneNumber', 'nok2_address',
        ]
        widgets = {
            'ippisNumber': forms.TextInput(attrs={'readonly': 'readonly'}),
            'fileNumber': forms.TextInput(attrs={'readonly': 'readonly'}),
            'lastName': forms.TextInput(attrs={'readonly': 'readonly'}),
            'firstName': forms.TextInput(attrs={'readonly': 'readonly'}),
            'middleName': forms.TextInput(attrs={'readonly': 'readonly'}),
            'dateOfBirth': forms.DateInput(attrs={'type': 'date', 'readonly': 'readonly'}),
            'dateOfFirstAppointment': forms.DateInput(attrs={'type': 'date', 'readonly': 'readonly'}),
            'dateOfBirth_ippis': forms.DateInput(attrs={'type': 'date', 'class': 'datepicker-input'}),
            'dateOfFirstAppointment_ippis': forms.DateInput(attrs={'type': 'date', 'class': 'datepicker-input'}),
            'dateOfPresentAppointment': forms.DateInput(attrs={'type': 'date', 'class': 'datepicker-input'}),
            'dateOfConfirmation': forms.DateInput(attrs={'type': 'date', 'class': 'datepicker-input'}),
            'lastPromotionDate': forms.DateInput(attrs={'type': 'date', 'class': 'datepicker-input'}),
            'stateOfOrigin': forms.Select(),
            'lgaOfOrigin': forms.Select(),
            'department': forms.Select(),
            'cadre': forms.Select(choices=OfficialAppointment.CADRE_CHOICES),
            'division': forms.Select(),
            'currentGradeLevel': forms.Select(),
            'stateOfPosting': forms.Select(),
            'station': forms.Select(),
            'presentAppointment': forms.Select(),
            'nok1_relationship': forms.Select(choices=Employee.NOK_RELATIONSHIP_CHOICES),
            'nok2_relationship': forms.Select(choices=Employee.NOK_RELATIONSHIP_CHOICES),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field not in ['ippisNumber', 'fileNumber', 'dateOfBirth', 'dateOfFirstAppointment']:
                self.fields[field].widget.attrs['class'] = 'form-input'
            else:   
                self.fields[field].widget.attrs['class'] = 'form-input bg-green-100'

        # Initialize querysets
        self.fields['stateOfOrigin'].queryset = State.objects.all()
        self.fields['stateOfPosting'].queryset = State.objects.all()
        self.fields['department'].queryset = Department.objects.all()
        self.fields['currentGradeLevel'].queryset = GradeLevel.objects.all()

        # Set up initial values for dependent fields
        if self.instance.pk:
            self.fields['lgaOfOrigin'].queryset = LGA.objects.filter(state=self.instance.stateOfOrigin)
            self.fields['station'].queryset = LGA.objects.filter(state=self.instance.stateOfPosting)
            self.fields['division'].queryset = Division.objects.filter(department=self.instance.department)
            self.fields['presentAppointment'].queryset = OfficialAppointment.objects.filter(department=self.instance.department)

        # If the form is bound, update the querysets based on the POST data
        if self.is_bound:
            if 'stateOfOrigin' in self.data:
                try:
                    state_id = int(self.data.get('stateOfOrigin'))
                    self.fields['lgaOfOrigin'].queryset = LGA.objects.filter(state_id=state_id)
                except (ValueError, TypeError):
                    pass
            if 'stateOfPosting' in self.data:
                try:
                    state_id = int(self.data.get('stateOfPosting'))
                    self.fields['station'].queryset = LGA.objects.filter(state_id=state_id)
                except (ValueError, TypeError):
                    pass
            if 'department' in self.data:
                try:
                    department_id = int(self.data.get('department'))
                    self.fields['division'].queryset = Division.objects.filter(department_id=department_id)
                    self.fields['presentAppointment'].queryset = OfficialAppointment.objects.filter(department_id=department_id)
                except (ValueError, TypeError):
                    pass
        
        # Make fields required
        required_fields = [
            'surname_ippis','firstName_ippis',
            'dateOfBirth_ippis', 'gender', 'maritalStatus', 'phoneNumber',
            'stateOfOrigin', 'lgaOfOrigin', 'dateOfFirstAppointment_ippis',
            'currentGradeLevel', 'department', 'stateOfPosting', 'station',
            'cadre', 'bank', 'accountNumber', 'accountType',
        ]
        for field in required_fields:
            self.fields[field].required = True

        for field_name, field in self.fields.items():
            if field.widget.attrs.get('readonly'):
                field.widget.attrs['class'] = 'bg-gray-100 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
            elif isinstance(field.widget, forms.DateInput):
                field.widget.attrs['class'] = 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full pl-10 p-2.5 datepicker-input'
                field.input_formats = ['%Y-%m-%d']  # Ensure consistent date format
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs['class'] = 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
            else:
                field.widget.attrs['class'] = 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
            
            field.widget.attrs['data-field-name'] = field_name  # Add this for client-side validation


    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data

class CompleteVerificationForm(forms.Form):
    captured_image = forms.CharField(widget=forms.HiddenInput, required=False)
    verification_notes = forms.CharField(widget=forms.Textarea)
    attestation = forms.BooleanField(required=True, label="I attest that I have truthfully verified this employee's information.")
    
    
    

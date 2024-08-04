import os
from django.conf import settings
from django.db.models import Q
from io import BytesIO
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.shortcuts import *
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from django.views.generic import *
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse, reverse_lazy
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from .models import *
from .forms import *
from django.db.models import Q, Count
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import csv
from io import StringIO
from django.contrib import messages
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from django.contrib.auth.views import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
# Create your views here.


def homepage(request):
    context = {
        'welcome_message': 'Welcome to Your Django Project!',
        'description': 'This is the home page of your new website.',
    }
    return render(request, 'hr_app/homepage.html', context)


class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff

# Custom User Views and Forms


class UserListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = User
    template_name = 'hr_app/user_list.html'
    context_object_name = 'users'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('q', '')
        if search_query:
            queryset = queryset.filter(
                Q(username__icontains=search_query) |
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(email__icontains=search_query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        return context


class UserDetailView(LoginRequiredMixin, StaffRequiredMixin, DetailView):
    model = User
    template_name = 'hr_app/user_detail.html'
    context_object_name = 'user'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['userprofile'] = self.object.userprofile
        return context


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name',
                  'last_name', 'is_staff', 'is_active']


class UserCreateView(SuccessMessageMixin, CreateView):
    form_class = UserCreateForm
    template_name = 'hr_app/user_form.html'
    success_url = reverse_lazy('user_list')
    success_message = "User %(username)s was created successfully"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create New User'
        return context


class UserUpdateView(SuccessMessageMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'hr_app/user_form.html'
    success_url = reverse_lazy('user_list')
    success_message = "User %(username)s was updated successfully"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Update User: {self.object.username}'
        return context


class UserDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = User
    template_name = 'hr_app/user_confirm_delete.html'
    success_url = reverse_lazy('user_list')

# Custom UserProfile Views and Forms


class UserProfileListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = UserProfile
    template_name = 'hr_app/userprofile_list.html'
    context_object_name = 'userprofiles'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('q', '')
        if search_query:
            queryset = queryset.filter(
                Q(user__username__icontains=search_query) |
                Q(user__first_name__icontains=search_query) |
                Q(user__last_name__icontains=search_query) |
                Q(user__email__icontains=search_query) |
                Q(phoneNumber__icontains=search_query) |
                Q(role__icontains=search_query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        return context


class UserProfileDetailView(LoginRequiredMixin, StaffRequiredMixin, DetailView):
    model = UserProfile
    template_name = 'hr_app/userprofile_detail.html'
    context_object_name = 'userprofile'


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['role', 'phoneNumber', 'ippisNumber', 'department',
                  'stateOfPosting', 'allowedStates', 'allowedDepartments', 'allowedZones']


class UserProfileCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'hr_app/userprofile_form.html'
    success_url = reverse_lazy('userprofile_list')


class UserProfileUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'hr_app/userprofile_form.html'
    success_url = reverse_lazy('userprofile_list')


class UserProfileDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = UserProfile
    template_name = 'hr_app/userprofile_confirm_delete.html'
    success_url = reverse_lazy('userprofile_list')

# Import Users from CSV


@user_passes_test(lambda u: u.userprofile.role == 'SUPER_ADMIN')
def import_users(request):
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        if csv_file.name.endswith('.csv'):
            try:
                data = csv_file.read().decode('utf-8')
                io_string = StringIO(data)
                reader = csv.reader(io_string, delimiter=',', quotechar='"')
                next(reader)  # Skip header row

                # Start transaction to ensure all operations succeed or fail together
                with transaction.atomic():
                    for row in reader:
                        (
                            username, email, first_name, last_name,
                            password, phoneNumber, role, department_code,
                            state_of_posting_code, allowed_states_codes,
                            allowed_departments_codes, allowed_zones_codes
                        ) = row

                        # Create user if they don't exist
                        user, created = User.objects.get_or_create(
                            username=username, email=email
                        )
                        # Set user attributes
                        user.first_name = first_name
                        user.last_name = last_name
                        user.set_password(password)
                        user.save()

                        # Get or create department, state, and zones
                        department, _ = Department.objects.get_or_create(
                            code=department_code
                        )
                        state_of_posting, _ = State.objects.get_or_create(
                            code=state_of_posting_code
                        )
                        allowed_states = State.objects.filter(
                            code__in=allowed_states_codes.split(
                                ',') if allowed_states_codes else []
                        )
                        allowed_departments = Department.objects.filter(
                            code__in=allowed_departments_codes.split(
                                ',') if allowed_departments_codes else []
                        )
                        allowed_zones = Zone.objects.filter(
                            code__in=allowed_zones_codes.split(
                                ',') if allowed_zones_codes else []
                        )

                        # Create/update UserProfile with provided data
                        profile, created = UserProfile.objects.get_or_create(
                            user=user)
                        profile.phoneNumber = phoneNumber
                        profile.role = role
                        profile.department = department
                        profile.stateOfPosting = state_of_posting
                        profile.allowedStates.set(allowed_states)
                        profile.allowedDepartments.set(allowed_departments)
                        profile.allowedZones.set(allowed_zones)
                        profile.save()
                messages.success(request, "Users imported successfully.")
                return redirect('user_list')
            except Exception as e:
                messages.error(request, f"Error importing users: {e}")
        else:
            messages.error(
                request, "Invalid file type. Please upload a .csv file.")
    return render(request, 'hr_app/import_users.html')

# Generic Views for other models


class GenericListView(LoginRequiredMixin, ListView):
    paginate_by = 10
    template_name = 'hr_app/generic_list.html'

    def get_url_name(self, suffix):
        """Generate URL name from model name."""
        model_name = self.model._meta.model_name.lower()
        return f"{model_name.replace(' ', '').replace('_', '')}{suffix}"

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('q', '')
        if search_query:
            # Adjust these fields as needed
            fields_to_search = ['name', 'code']
            q_objects = Q()
            for field in fields_to_search:
                q_objects |= Q(**{f'{field}__icontains': search_query})
            queryset = queryset.filter(q_objects)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'model_name': self.model._meta.verbose_name,
            'model_name_plural': self.model._meta.verbose_name_plural,
            'can_add': self.request.user.is_staff,
            'detail_url_name': self.get_url_name('_detail'),
            'edit_url_name': self.get_url_name('_edit'),
            'add_url_name': self.get_url_name('_add'),
            'delete_url_name': self.get_url_name('_delete'),
            'list_url_name': self.get_url_name('_list'),
            'search_query': self.request.GET.get('q', ''),
            'model': self.model,
            'pk_field': self.model._meta.pk.name,
        })
        return context


class GenericDetailView(LoginRequiredMixin, DetailView):
    template_name = 'hr_app/generic_detail.html'

    def get_visible_fields(self):
        return [field for field in self.object._meta.get_fields() if not field.is_relation and field.name != 'id']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model_name = self.model._meta.model_name
        context.update({
            'model_name': self.model._meta.verbose_name,
            'can_edit': self.request.user.is_staff,
            'edit_url': reverse_lazy(f'{model_name}_edit', kwargs={'pk': self.object.pk}),
            'list_url': reverse_lazy(f'{model_name}_list'),
            'visible_fields': self.get_visible_fields(),
        })
        return context


class GenericFormView(LoginRequiredMixin, StaffRequiredMixin):
    template_name = 'hr_app/generic_form.html'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.helper = FormHelper()
        form.helper.layout = Layout(
            *[Row(Column(field, css_class='form-group col-md-12 mb-0'))
              for field in form.fields]
        )
        form.helper.add_input(Submit(
            'submit', 'Save', css_class='bg-[#1d741b] hover:bg-[#ab8206] text-white font-semibold py-2 px-4 rounded-full transition duration-300 ease-in-out mt-4'))
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'model_name': self.model._meta.verbose_name,
            'action': 'Create' if isinstance(self, CreateView) else 'Update',
            'list_url': reverse_lazy(f'{self.model._meta.model_name}_list'),
        })
        return context

    def form_valid(self, form):
        messages.success(
            self.request, f"{self.model._meta.verbose_name} {'created' if isinstance(self, CreateView) else 'updated'} successfully.")
        return super().form_valid(form)


class GenericCreateView(GenericFormView, CreateView):
    pass


class GenericUpdateView(GenericFormView, UpdateView):
    pass


class GenericUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    template_name = 'hr_app/generic_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'model_name': self.model._meta.verbose_name,
            'action': 'Update',
            'list_url': reverse_lazy(f'{self.model._meta.model_name}_list'),
        })
        return context

    def form_valid(self, form):
        messages.success(
            self.request, f"{self.model._meta.verbose_name} updated successfully.")
        return super().form_valid(form)


class GenericDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    template_name = 'hr_app/generic_confirm_delete.html'

# State Views


class StateListView(GenericListView):
    model = State
    context_object_name = 'objects'


class StateDetailView(GenericDetailView):
    model = State


class StateCreateView(GenericCreateView):
    model = State
    form_class = StateForm
    success_url = reverse_lazy('state_list')


class StateUpdateView(GenericUpdateView):
    model = State
    form_class = StateForm
    success_url = reverse_lazy('state_list')


class StateDeleteView(GenericDeleteView):
    model = State
    success_url = reverse_lazy('state_list')

# LGA Views


class LGAListView(GenericListView):
    model = LGA
    context_object_name = 'objects'


class LGADetailView(GenericDetailView):
    model = LGA


class LGACreateView(GenericCreateView):
    model = LGA
    form_class = LGAForm
    success_url = reverse_lazy('lga_list')


class LGAUpdateView(GenericUpdateView):
    model = LGA
    form_class = LGAForm
    success_url = reverse_lazy('lga_list')


class LGADeleteView(GenericDeleteView):
    model = LGA
    success_url = reverse_lazy('lga_list')

# Division Views


class DivisionListView(GenericListView):
    model = Division
    context_object_name = 'objects'


class DivisionDetailView(GenericDetailView):
    model = Division


class DivisionCreateView(GenericCreateView):
    model = Division
    form_class = DivisionForm
    success_url = reverse_lazy('division_list')


class DivisionUpdateView(GenericUpdateView):
    model = Division
    form_class = DivisionForm
    success_url = reverse_lazy('division_list')


class DivisionDeleteView(GenericDeleteView):
    model = Division
    success_url = reverse_lazy('division_list')

# Department Views


class DepartmentListView(GenericListView):
    model = Department
    context_object_name = 'objects'


class DepartmentDetailView(GenericDetailView):
    model = Department


class DepartmentCreateView(GenericCreateView):
    model = Department
    form_class = DepartmentForm
    success_url = reverse_lazy('department_list')


class DepartmentUpdateView(GenericUpdateView):
    model = Department
    form_class = DepartmentForm
    success_url = reverse_lazy('department_list')


class DepartmentDeleteView(GenericDeleteView):
    model = Department
    success_url = reverse_lazy('department_list')

# Grade Level Views


class GradeLevelListView(GenericListView):
    model = GradeLevel
    context_object_name = 'objects'


class GradeLevelDetailView(GenericDetailView):
    model = GradeLevel


class GradeLevelCreateView(GenericCreateView):
    model = GradeLevel
    form_class = GradeLevelForm
    success_url = reverse_lazy('gradelevel_list')


class GradeLevelUpdateView(GenericUpdateView):
    model = GradeLevel
    form_class = GradeLevelForm
    success_url = reverse_lazy('gradelevel_list')


class GradeLevelDeleteView(GenericDeleteView):
    model = GradeLevel
    success_url = reverse_lazy('gradelevel_list')

# Official Appointment Views


class OfficialAppointmentListView(GenericListView):
    model = OfficialAppointment


class OfficialAppointmentDetailView(GenericDetailView):
    model = OfficialAppointment


class OfficialAppointmentCreateView(GenericCreateView):
    model = OfficialAppointment
    fields = ['code', 'name', 'gradeLevel', 'cadre', 'department']
    success_url = reverse_lazy('officialappointment_list')


class OfficialAppointmentUpdateView(GenericUpdateView):
    model = OfficialAppointment
    fields = ['name', 'gradeLevel', 'cadre', 'department']
    success_url = reverse_lazy('officialappointment_list')


class OfficialAppointmentDeleteView(GenericDeleteView):
    model = OfficialAppointment
    success_url = reverse_lazy('officialappointment_list')


class HomepageView(TemplateView):
    template_name = 'hr_app/homepage.html'


class UserLoginView(LoginView):
    form_class = UserLoginForm
    template_name = 'hr_app/user_login.html'
    # You'll need to create this view
    success_url = reverse_lazy('admin_dashboard')


from django.contrib.auth.forms import AuthenticationForm

def admin_login(request):
    if request.method == 'POST':
        form = AdminLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None and user.is_staff:
                login(request, user)
                return redirect('admin_dashboard')
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = AdminLoginForm()
    return render(request, 'hr_app/admin_login.html', {'form': form})

@login_required
def profile(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('profile')
    else:
        form = UserProfileForm(instance=user_profile)
    return render(request, 'hr_app/profile.html', {'form': form, 'user_profile': user_profile})


@login_required
def employee_profile(request):
    employee = get_object_or_404(Employee, user=request.user)
    
    if request.method == 'POST':
        form = EmployeeProfileForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully.")
            return redirect('employee_profile')
    else:
        form = EmployeeProfileForm(instance=employee)
    
    context = {
        'employee': employee,
        'form': form,
    }
    return render(request, 'hr_app/employee_profile.html', context)


# views.py


def employee_login(request):
    if request.method == 'POST':
        form = EmployeeLoginForm(request.POST)
        if form.is_valid():
            ippis_number = form.cleaned_data['ippis_number']
            print(f"IPPIS Number entered: {ippis_number}")

            staff_audit = StaffAuditEmployee.objects.filter(
                ippisNumber__iexact=ippis_number).first()

            if staff_audit:
                print(f"Staff Audit Found: {staff_audit}")
                if staff_audit.isProcessed:
                    employee, created = Employee.objects.get_or_create(
                        ippisNumber=ippis_number)
                    request.session['employee_id'] = employee.id
                    return redirect('employee_summary', ippis_number=ippis_number)
                else:
                    request.session['staff_audit_id'] = staff_audit.id
                    return redirect('employee_data', ippis_number=ippis_number)
            else:
                messages.error(request, "No record found for this IPPIS number.")
    else:
        form = EmployeeLoginForm()
    return render(request, 'hr_app/employee_login.html', {'form': form})


def employee_summary(request, ippis_number):
    staff_audit = get_object_or_404(StaffAuditEmployee, ippisNumber=ippis_number)

    if request.method == 'POST':
        if request.POST.get('confirm') == 'on':
            staff_audit.isProcessed = True
            staff_audit.processedDate = timezone.now()
            staff_audit.save()
            employee, created = Employee.objects.get_or_create(
                ippisNumber=ippis_number)
            request.session['employee_id'] = employee.id
            return redirect('employee_dashboard', ippis_number=ippis_number)

    return render(request, 'hr_app/employee_summary.html', {'staff_audit': staff_audit})
# views.py


def employee_dashboard(request, ippis_number):
    employee = get_object_or_404(Employee, ippisNumber=ippis_number)
    
    # Calculate the completion percentage
    total_sections = 6 if employee.maritalStatus != 'M' else 7
    completed_sections = sum([
        employee.isPersonalInfoUpdated,
        employee.isEmploymentInfoUpdated,
        employee.isEducationInfoUpdated,
        employee.isPreviousEmploymentUpdated,
        employee.isNextOfKinUpdated,
        employee.financialInfoUpdated,
        employee.isSpouseInfoUpdated if employee.maritalStatus == 'M' else 0
    ])
    completion_percentage = (completed_sections / total_sections) * 100

    context = {
        'employee': employee,
        'completion_percentage': completion_percentage,
        'sections': [
            {
                'name': 'Personal Information',
                'url': reverse('update_personal_info', args=[ippis_number]),
                'is_completed': employee.isPersonalInfoUpdated,
                'description': 'Update your basic personal details including name, date of birth, and contact information.'
            },
            {
                'name': 'Employment Information',
                'url': reverse('update_employment_info', args=[ippis_number]),
                'is_completed': employee.isEmploymentInfoUpdated,
                'description': 'Provide details about your current employment status, position, and department.'
            },
            {
                'name': 'Education Information',
                'url': reverse('update_education_info', args=[ippis_number]),
                'is_completed': employee.isEducationInfoUpdated,
                'description': 'Add your educational qualifications and certifications.'
            },
            {
                'name': 'Previous Employment',
                'url': reverse('update_previous_employment', args=[ippis_number]),
                'is_completed': employee.isPreviousEmploymentUpdated,
                'description': 'List your work experience prior to your current position.'
            },
            {
                'name': 'Next of Kin',
                'url': reverse('update_next_of_kin', args=[ippis_number]),
                'is_completed': employee.isNextOfKinUpdated,
                'description': 'Provide contact information for your next of kin.'
            },
            {
                'name': 'Financial Information',
                'url': reverse('update_financial_info', args=[ippis_number]),
                'is_completed': employee.financialInfoUpdated,
                'description': 'Update your bank account and pension fund details.'
            },
        ]
    }
    
    # Add spouse information section only if the employee is married
    if employee.maritalStatus == 'M':
        context['sections'].append({
            'name': 'Spouse Information',
            'url': reverse('update_spouse_info', args=[ippis_number]),
            'is_completed': employee.isSpouseInfoUpdated,
            'description': 'Provide details about your spouse.'
        })

    return render(request, 'hr_app/employee_dashboard.html', context)


def update_personal_info(request, ippis_number):
    employee = get_object_or_404(Employee, ippisNumber=ippis_number)
    staff_audit = StaffAuditEmployee.objects.filter(ippisNumber=ippis_number).first()

    if request.method == 'POST':
        form = PersonalInfoForm(request.POST, request.FILES, instance=employee)
        if form.is_valid():
            form.save()
            employee.isPersonalInfoUpdated = True
            employee.save()
            messages.success(request, 'Personal information updated successfully.')
            return redirect('employee_dashboard', ippis_number=ippis_number)
    else:
        initial_data = {}
        if not employee.isPersonalInfoUpdated and staff_audit:
            initial_data = {
                'fileNumber': staff_audit.fileNumber,
                'firstName': staff_audit.otherNames.split()[0] if staff_audit.otherNames else '',
                'lastName': staff_audit.surname,
                'middleName': ' '.join(staff_audit.otherNames.split()[1:]) if staff_audit.otherNames else '',
                'dateOfBirth': staff_audit.dateOfBirth,
                'gender': staff_audit.sex,
                'maritalStatus': staff_audit.maritalStatus,
                'phoneNumber': staff_audit.phoneNumber,
                'stateOfOrigin': staff_audit.stateOfOrigin,
                'lgaOfOrigin': staff_audit.lgaOfOrigin,
            }
        form = PersonalInfoForm(instance=employee, initial=initial_data)

    return render(request, 'hr_app/update_personal_info.html', {'form': form, 'employee': employee})


def update_employment_info(request, ippis_number):
    employee = get_object_or_404(Employee, ippisNumber=ippis_number)
    staff_audit = StaffAuditEmployee.objects.filter(
        ippisNumber=ippis_number).first()

    if request.method == 'POST':
        form = EmploymentInfoForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            employee.isEmploymentInfoUpdated = True
            employee.save()
            
            # Generate Discrepancies after saving employment info
            if staff_audit:  # Make sure a staff_audit record exists
                discrepancies = staff_audit.compareWithEmployee(employee)
                for discrepancy in discrepancies:
                    Discrepancy.objects.create(
                        employee=employee,
                        discrepancyType=discrepancy['type'],
                        auditValue=discrepancy['auditValue'],
                        employeeValue=discrepancy['employeeValue']
                    )
                    
                    
            messages.success(
                request, 'Employment information updated successfully.')
            return redirect('employee_dashboard', ippis_number=ippis_number)
    else:
        initial_data = {}
        if not employee.isEmploymentInfoUpdated and staff_audit:
            initial_data = {
                'fileNumber': staff_audit.fileNumber,
                'dateOfFirstAppointment': staff_audit.dateOfFirstAppointment,
                'dateOfPresentAppointment': staff_audit.dateOfPresentAppointment,
                'dateOfConfirmation': staff_audit.dateOfConfirmation,
                'cadre': staff_audit.cadre,
                'currentGradeLevel': staff_audit.gradeLevel,
                'currentStep': staff_audit.step,
                'department': staff_audit.department,
                'stateOfPosting': staff_audit.stateOfPosting,
            }
        form = EmploymentInfoForm(instance=employee, initial=initial_data)

    return render(request, 'hr_app/update_employment_info.html', {'form': form, 'employee': employee})


def update_education_info(request, ippis_number):
    employee = get_object_or_404(Employee, ippisNumber=ippis_number)
    
    if request.method == 'POST':
        formset = EducationFormSet(request.POST, instance=employee)
        if formset.is_valid():
            instances = formset.save(commit=False)
            for instance in instances:
                instance.employee = employee
                instance.save()
            formset.save_m2m()
            employee.isEducationInfoUpdated = True
            employee.save()
            messages.success(request, 'Education information updated successfully.')
            return redirect('employee_dashboard', ippis_number=ippis_number)
    else:
        formset = EducationFormSet(instance=employee)

    return render(request, 'hr_app/update_education_info.html', {'formset': formset, 'employee': employee})


def update_previous_employment(request, ippis_number):
    employee = get_object_or_404(Employee, ippisNumber=ippis_number)

    if request.method == 'POST':
        formset = PreviousEmploymentFormSet(request.POST, instance=employee)
        if formset.is_valid():
            formset.save()
            employee.isPreviousEmploymentUpdated = True
            employee.save()
            messages.success(
                request, 'Previous employment information updated successfully.')
            return redirect('employee_dashboard', ippis_number=ippis_number)
    else:
        formset = PreviousEmploymentFormSet(instance=employee)

    return render(request, 'hr_app/update_previous_employment.html', {'formset': formset, 'employee': employee})


def update_next_of_kin(request, ippis_number):
    employee = get_object_or_404(Employee, ippisNumber=ippis_number)
    next_of_kin, created = NextOfKin.objects.get_or_create(employee=employee)
    staff_audit = StaffAuditEmployee.objects.filter(
        ippisNumber=ippis_number).first()

    if request.method == 'POST':
        form = NextOfKinForm(request.POST, instance=next_of_kin)
        if form.is_valid():
            form.save()
            employee.isNextOfKinUpdated = True
            employee.save()
            messages.success(
                request, 'Next of kin information updated successfully.')
            return redirect('employee_dashboard', ippis_number=ippis_number)
    else:
        initial_data = {}
        if not employee.isNextOfKinUpdated and staff_audit:
            initial_data = {
                'nok1_name': staff_audit.nok1_name,
                'nok1_relationship': staff_audit.nok1_relationship,
                'nok1_address': staff_audit.nok1_address,
                'nok1_phoneNumber': staff_audit.nok1_phoneNumber,
                'nok2_name': staff_audit.nok2_name,
                'nok2_relationship': staff_audit.nok2_relationship,
                'nok2_address': staff_audit.nok2_address,
                'nok2_phoneNumber': staff_audit.nok2_phoneNumber,
            }
        form = NextOfKinForm(instance=next_of_kin, initial=initial_data)

    return render(request, 'hr_app/update_next_of_kin.html', {'form': form, 'employee': employee})


def update_financial_info(request, ippis_number):
    employee = get_object_or_404(Employee, ippisNumber=ippis_number)
    staff_audit = StaffAuditEmployee.objects.filter(
        ippisNumber=ippis_number).first()

    if request.method == 'POST':
        form = FinancialInfoForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            employee.financialInfoUpdated = True
            employee.save()
            messages.success(
                request, 'Financial information updated successfully.')
            return redirect('employee_dashboard', ippis_number=ippis_number)
    else:
        initial_data = {}
        if not employee.financialInfoUpdated and staff_audit:
            initial_data = {
                'bank': staff_audit.bank,
                'accountType': staff_audit.accountType,
                'accountNumber': staff_audit.accountNumber,
                'pfa': staff_audit.pfa,
                'pfaNumber': staff_audit.pfaNumber,
            }
        form = FinancialInfoForm(instance=employee, initial=initial_data)

    return render(request, 'hr_app/update_financial_info.html', {'form': form, 'employee': employee})


def update_spouse_info(request, ippis_number):
    employee = get_object_or_404(Employee, ippisNumber=ippis_number)

    if request.method == 'POST':
        form = SpouseInfoForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            employee.isSpouseInfoUpdated = True
            employee.save()
            messages.success(
                request, 'Spouse information updated successfully.')
            return redirect('employee_dashboard', ippis_number=ippis_number)
    else:
        form = SpouseInfoForm(instance=employee)

    return render(request, 'hr_app/update_spouse_info.html', {'form': form, 'employee': employee})


def employee_data_sheet(request):
    employee_id = request.session.get('employee_id')
    employee = get_object_or_404(Employee, id=employee_id)
    return render(request, 'employee_data_sheet.html', {'employee': employee})


def employee_data(request):
    employee_id = request.session.get('employee_id')
    employee = get_object_or_404(Employee, id=employee_id)
    next_of_kin = get_object_or_404(NextOfKin, employee=employee)
    

    # Define fields to display and their values
    personal_fields = [
        {'label': 'Full Name', 'value': f'{employee.firstName} {employee.lastName}'},
        {'label': 'Middle Name', 'value': employee.middleName},
        {'label': 'IPPIS Number', 'value': employee.ippisNumber},
        {'label': 'File Number', 'value': employee.fileNumber},
        {'label': 'Date of Birth', 'value': employee.dateOfBirth},
        {'label': 'Gender', 'value': dict(Employee.GENDER_CHOICES)[employee.gender]},
        {'label': 'Marital Status', 'value': dict(Employee.MARITAL_STATUS_CHOICES)[employee.maritalStatus]},
        {'label': 'Phone Number', 'value': employee.phoneNumber},
        {'label': 'Email Address', 'value': employee.emailAddress},
        {'label': 'Residential Address', 'value': employee.residentialAddress},
        {'label': 'State of Origin', 'value': employee.stateOfOrigin},
        {'label': 'LGA of Origin', 'value': employee.lgaOfOrigin},
        {'label': 'NIN', 'value': employee.nin},
    ]

    employment_fields = [
        {'label': 'Date of First Appointment', 'value': employee.dateOfFirstAppointment},
        {'label': 'Date of Present Appointment', 'value': employee.dateOfPresentAppointment},
        {'label': 'Date of Confirmation', 'value': employee.dateOfConfirmation},
        {'label': 'Cadre', 'value': dict(Employee.CADRE_CHOICES)[employee.cadre]},
        {'label': 'Current Grade Level', 'value': employee.currentGradeLevel},
        {'label': 'Current Step', 'value': employee.currentStep},
        {'label': 'Department', 'value': employee.department},
        {'label': 'Division', 'value': employee.division},
        {'label': 'State of Posting', 'value': employee.stateOfPosting},
        {'label': 'Station', 'value': employee.station},
        {'label': 'Present Appointment', 'value': employee.presentAppointment},
        {'label': 'Last Promotion Date', 'value': employee.lastPromotionDate},
        {'label': 'Retirement Date', 'value': employee.calculate_retirementDate()},
        {'label': 'Is On Leave', 'value': employee.isOnLeave},
        {'label': 'Is Under Disciplinary Action', 'value': employee.isUnderDisciplinaryAction},
    ]

    financial_fields = [
        {'label': 'Bank', 'value': employee.bank},
        {'label': 'Account Type', 'value': dict(Employee.ACCOUNT_TYPES)[employee.accountType]},
        {'label': 'Account Number', 'value': employee.accountNumber},
        {'label': 'PFA', 'value': employee.pfa},
        {'label': 'PFA Number', 'value': employee.pfaNumber},
    ]

    spouse_fields = [
        {'label': 'Spouse Full Name', 'value': employee.spouse_fullName},
        {'label': 'Spouse Occupation', 'value': employee.spouse_occupation},
        {'label': 'Spouse Employer Name', 'value': employee.spouse_employerName},
        {'label': 'Spouse Employment Period', 'value': employee.spouse_employmentPeriod},
    ]

    # Fetch next of kin data
    nok_fields = [
        {'label': 'NOK 1 Full Name', 'value': next_of_kin.nok1_fullName if next_of_kin else None},
        {'label': 'NOK 1 Relationship', 'value': dict(NextOfKin.RELATIONSHIP_CHOICES)[next_of_kin.nok1_relationship] if next_of_kin else None},
        {'label': 'NOK 1 Address', 'value': next_of_kin.nok1_address if next_of_kin else None},
        {'label': 'NOK 1 Phone Number', 'value': next_of_kin.nok1_phoneNumber if next_of_kin else None},
        {'label': 'NOK 2 Full Name', 'value': next_of_kin.nok2_fullName if next_of_kin else None},
        {'label': 'NOK 2 Relationship', 'value': dict(NextOfKin.RELATIONSHIP_CHOICES)[next_of_kin.nok2_relationship] if next_of_kin else None},
        {'label': 'NOK 2 Address', 'value': next_of_kin.nok2_address if next_of_kin else None},
        {'label': 'NOK 2 Phone Number', 'value': next_of_kin.nok2_phoneNumber if next_of_kin else None},
    ]

    education_fields = []
    for education in EducationAndTraining.objects.filter(employee=employee).all():
        education_fields.append({
            'label': 'Education & Training',
            'value': f"{education.activityType} - {education.title} ({education.level}) at {education.institution}"
        })

    previous_employment_fields = []
    for employment in PreviousEmployment.objects.filter(employee=employee).all():
        previous_employment_fields.append({
            'label': 'Previous Employment',
            'value': f"Organisation: {employment.organisation}, Position: {employment.position},Start Date: {employment.startDate}, End Date: {employment.endDate}"
        })

    context = {
        'employee': employee,
        'personal_fields': personal_fields,
        'employment_fields': employment_fields,
        'financial_fields': financial_fields,
        'spouse_fields': spouse_fields,
        'nok_fields': nok_fields,
        'education_fields': education_fields,
        'previous_employment_fields': previous_employment_fields,
    }

    return render(request, 'hr_app/employee_data.html', context)


def link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those
    resources
    """
    sUrl = settings.STATIC_URL
    sRoot = settings.STATIC_ROOT
    mUrl = settings.MEDIA_URL
    mRoot = settings.MEDIA_ROOT

    if uri.startswith(mUrl):
        path = os.path.join(mRoot, uri.replace(mUrl, ""))
    elif uri.startswith(sUrl):
        path = os.path.join(sRoot, uri.replace(sUrl, ""))
    else:
        return uri

    if not os.path.isfile(path):
        raise Exception(
            'media URI must start with %s or %s' % (sUrl, mUrl)
        )
    return path


def generate_employee_pdf(request):
    employee_id = request.session.get('employee_id')
    employee = get_object_or_404(Employee.objects.select_related(
        'stateOfOrigin',
        'lgaOfOrigin',
        'department',
        'stateOfPosting',
    ), id=employee_id)

    # Fetch related models
    next_of_kin = NextOfKin.objects.filter(employee=employee).first()
    education_and_training = EducationAndTraining.objects.filter(employee=employee)
    previous_employments = PreviousEmployment.objects.filter(employee=employee)

    template = get_template('hr_app/employee_pdf_template.html')
    context = {
        'employee': employee,
        'next_of_kin': next_of_kin,
        'education_and_training': education_and_training,
        'previous_employments': previous_employments,
        'STATIC_URL': settings.STATIC_URL,
    }
    html = template.render(context)

    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result, link_callback=link_callback)

    if not pdf.err:
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{employee.firstName}_{employee.lastName}_{employee.ippisNumber}_data_sheet.pdf"'
        return response

    return HttpResponse('Error generating PDF', status=400)


# def generate_employee_pdf(request):
#     employee_id = request.session.get('employee_id')
#     employee = get_object_or_404(Employee, id=employee_id)

#     template = get_template('hr_app/employee_pdf_template.html')
#     context = {'employee': employee}
#     html = template.render(context)

#     result = BytesIO()
#     pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)

#     if not pdf.err:
#         response = HttpResponse(result.getvalue(), content_type='application/pdf')
#         response['Content-Disposition'] = f'attachment; filename="{employee.firstName}_{employee.lastName}_{employee.ippisNumber}_data_sheet.pdf"'
#         return response

#     return HttpResponse('Error generating PDF', status=400)


def employee_logout(request):
    request.session.flush()
    messages.success(request, "You have been successfully logged out.")
    return redirect('employee_login')


class EmployeeUpdateView(TemplateView):
    template_name = 'hr_app/employee_update.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ippis_number = self.request.session.get('ippis_number')
        employee, created = Employee.objects.get_or_create(
            ippisNumber=ippis_number)

        if created:
            staff_audit_employee = StaffAuditEmployee.objects.get(
                ippisNumber=ippis_number)
            for field in employee._meta.fields:
                if hasattr(staff_audit_employee, field.name):
                    setattr(employee, field.name, getattr(
                        staff_audit_employee, field.name))
            employee.save()

        context['employee'] = employee
        context['personal_form'] = PersonalInfoForm(
            instance=employee, prefix='personal')
        context['employment_form'] = EmploymentInfoForm(
            instance=employee, prefix='employment')
        context['spouse_form'] = SpouseInfoForm(
            instance=employee, prefix='spouse')
        context['next_of_kin_formset'] = NextOfKinFormSet(
            instance=employee, prefix='nok')
        context['education_formset'] = EducationAndTrainingFormSet(
            instance=employee, prefix='education')
        context['financial_form'] = FinancialInfoForm(
            instance=employee, prefix='financial')
        context['previous_employment_formset'] = PreviousEmploymentFormSet(
            instance=employee, prefix='previous_employment')
        return context

    def post(self, request, *args, **kwargs):
        ippis_number = self.request.session.get('ippis_number')
        employee = Employee.objects.get(ippisNumber=ippis_number)

        forms = {
            'personal': PersonalInfoForm(request.POST, instance=employee, prefix='personal'),
            'employment': EmploymentInfoForm(request.POST, instance=employee, prefix='employment'),
            'spouse': SpouseInfoForm(request.POST, instance=employee, prefix='spouse'),
            'nok': NextOfKinFormSet(request.POST, instance=employee, prefix='nok'),
            'education': EducationAndTrainingFormSet(request.POST, instance=employee, prefix='education'),
            'financial': FinancialInfoForm(request.POST, instance=employee, prefix='financial'),
            'previous_employment': PreviousEmploymentFormSet(request.POST, instance=employee, prefix='previous_employment'),
        }

        if all(form.is_valid() for form in forms.values()):
            for form in forms.values():
                if isinstance(form, (NextOfKinFormSet, EducationAndTrainingFormSet, PreviousEmploymentFormSet)):
                    form.save()
                else:
                    form.save()
            employee.isProfileUpdated = True
            employee.save()
            messages.success(request, "All information updated successfully.")
            return redirect('employee_summary')
        else:
            for form in forms.values():
                if form.errors:
                    for field, error in form.errors.items():
                        messages.error(request, f"{field}: {error}")
            return self.render_to_response(self.get_context_data(**forms))


class EmployeeSummaryView(TemplateView):
    template_name = 'hr_app/employee_summary.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ippis_number = self.request.session.get('ippis_number')
        employee = Employee.objects.get(ippisNumber=ippis_number)
        context['employee'] = employee
        return context



class EmployeeVerificationView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Employee
    template_name = 'hr_app/employee_verification.html'
    context_object_name = 'employee'

    def test_func(self):
        return self.request.user.is_staff

    def post(self, request, *args, **kwargs):
        employee = self.get_object()
        action = request.POST.get('action')
        comments = request.POST.get('comments', '')

        if action == 'verify':
            employee.isVerified = True
            employee.verifiedBy = request.user
            employee.verificationDate = timezone.now()
            employee.verificationComments = comments
            employee.save()
            messages.success(
                request, f"Employee {employee.firstName} {employee.lastName} has been verified.")
        elif action == 'reject':
            employee.isVerified = False
            employee.verificationComments = comments
            employee.save()
            messages.warning(
                request, f"Employee {employee.firstName} {employee.lastName} verification has been rejected.")

        return redirect('employee_list')


class EmployeeListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Employee
    template_name = 'hr_app/employee_list.html'
    context_object_name = 'employees'
    paginate_by = 20

    def test_func(self):
        return self.request.user.is_staff

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(firstName__icontains=search_query) |
                Q(lastName__icontains=search_query) |
                Q(ippisNumber__icontains=search_query)
            )
        return queryset


class EmployeeCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Employee
    form_class = EmployeeForm
    template_name = 'hr_app/employee_form.html'
    success_url = reverse_lazy('employee_list')

    def test_func(self):
        return self.request.user.is_staff

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class EmployeeReportView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'hr_app/employee_report.html'

    def test_func(self):
        return self.request.user.is_staff

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_employees'] = Employee.objects.count()
        context['department_stats'] = Employee.objects.values(
            'department__name').annotate(count=Count('id'))
        context['grade_level_stats'] = Employee.objects.values(
            'currentGradeLevel__name').annotate(count=Count('id'))
        return context

    def post(self, request, *args, **kwargs):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="employee_report.csv"'

        writer = csv.writer(response)
        writer.writerow(['IPPIS Number', 'First Name',
                        'Last Name', 'Department', 'Grade Level'])

        employees = Employee.objects.all()
        for employee in employees:
            writer.writerow([
                employee.ippisNumber,
                employee.firstName,
                employee.lastName,
                employee.department.name if employee.department else '',
                employee.currentGradeLevel.name if employee.currentGradeLevel else ''
            ])

        return response
    

def is_authorized(user, allowed_roles):
    return user.is_authenticated and user.userprofile.role in allowed_roles


@login_required
def admin_dashboard(request):
    user_role = request.user.userprofile.role
    context = {
        'user_role': user_role,
        'total_employees': Employee.objects.count(),
        'pending_verifications': Employee.objects.filter(isVerified=False).count(),
        'open_discrepancies': Discrepancy.objects.filter(isResolved=False).count(),
        'total_departments': Employee.objects.values('department').distinct().count(),
    }

    if user_role in ['DRUID_VIEWER', 'SUPER_ADMIN']:
        context.update({
            'total_users': UserProfile.objects.count(),
            'user_role_counts': UserProfile.objects.values('role').annotate(count=Count('role')),
        })

    if user_role in ['DRUID_VIEWER', 'SUPER_ADMIN', 'DIRECTOR_GENERAL', 'HR_ADMIN']:
        context.update({
            'verification_progress': get_verification_progress(),
            'discrepancy_types': get_discrepancy_types(),
        })

    if user_role in ['DRUID_VIEWER', 'IT_ADMIN']:
        context.update({
            'system_health': get_system_health(),
        })

    if user_role in ['HR_DATA_SCREENING']:
        context.update({
            'duplicate_file_numbers': get_duplicate_file_numbers(),
        })

    if user_role in ['HELPDESK']:
        context.update({
            'open_tickets': Ticket.objects.filter(is_resolved=False).count(),
        })

    return render(request, 'hr_app/admin_dashboard.html', context)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Employee, Discrepancy, StaffAuditEmployee, NextOfKin, EducationAndTraining, PreviousEmployment
from .forms import EmployeeVerificationForm, DiscrepancyResolutionForm


@login_required
@user_passes_test(lambda u: is_authorized(u, ['DRUID_VIEWER', 'SUPER_ADMIN', 'DIRECTOR_GENERAL', 'HR_ADMIN', 'VERIFICATION_OFFICER']))
def manage_discrepancies(request):
    query = request.GET.get('query')
    discrepancies = Discrepancy.objects.all().order_by('-createdAt')

    if query:
        discrepancies = discrepancies.filter(
            Q(employee__firstName__icontains=query) |
            Q(employee__lastName__icontains=query) |
            Q(employee__ippisNumber__icontains=query) |
            Q(discrepancyType__icontains=query)
        )

    paginator = Paginator(discrepancies, 12)  # Show 12 discrepancies per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'query': query,
    }
    return render(request, 'hr_app/manage_discrepancies.html', context)

@login_required
@user_passes_test(lambda u: is_authorized(u, ['DRUID_VIEWER', 'SUPER_ADMIN', 'DIRECTOR_GENERAL', 'HR_ADMIN', 'VERIFICATION_OFFICER']))
def discrepancy_detail(request, discrepancy_id):
    discrepancy = get_object_or_404(Discrepancy, id=discrepancy_id)
    
    if request.method == 'POST':
        form = DiscrepancyForm(request.POST, instance=discrepancy)
        if form.is_valid():
            resolved_discrepancy = form.save(commit=False)
            resolved_discrepancy.isResolved = True
            resolved_discrepancy.resolvedBy = request.user
            resolved_discrepancy.resolutionDate = timezone.now()
            resolved_discrepancy.save()
            messages.success(request, "Discrepancy has been resolved.")
            return redirect('manage_discrepancies')
    else:
        form = DiscrepancyForm(instance=discrepancy)
    
    context = {
        'discrepancy': discrepancy,
        'form': form,
    }
    return render(request, 'hr_app/discrepancy_detail.html', context)



def is_authorized(user, roles):
    return user.is_authenticated and user.userprofile.role in roles

@login_required
@user_passes_test(lambda u: is_authorized(u, ['DRUID_VIEWER', 'SUPER_ADMIN', 'DIRECTOR_GENERAL', 'HR_ADMIN', 'VERIFICATION_OFFICER']))
def search_verify_employees(request):
    query = request.GET.get('query', '')
    employees = Employee.objects.all()

    if query:
        employees = employees.filter(
            Q(ippisNumber__icontains=query) |
            Q(emailAddress__icontains=query) |
            Q(phoneNumber__icontains=query) |
            Q(firstName__icontains=query) |
            Q(lastName__icontains=query)
        )

    employees = employees.filter(
        Q(stateOfPosting__in=request.user.userprofile.allowedStates.all()) &
        Q(department__in=request.user.userprofile.allowedDepartments.all())
    )

    paginator = Paginator(employees, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'query': query,
        'employees': page_obj,
    }
    return render(request, 'hr_app/search_verify_employees.html', context)

@login_required
@user_passes_test(lambda u: is_authorized(u, ['DRUID_VIEWER', 'SUPER_ADMIN', 'DIRECTOR_GENERAL', 'HR_ADMIN', 'VERIFICATION_OFFICER']))
def employee_detail(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    staff_audit = StaffAuditEmployee.objects.filter(ippisNumber=employee.ippisNumber).first()
    discrepancies = Discrepancy.objects.filter(employee=employee, isResolved=False)

    personal_fields = {
        'IPPIS Number': employee.ippisNumber,
        'File Number': employee.fileNumber,
        'Date of Birth': employee.dateOfBirth,
        'Email': employee.emailAddress,
        'State of Origin': employee.stateOfOrigin,
        'LGA of Origin': employee.lgaOfOrigin,
        'Phone': employee.phoneNumber,
        'Gender': employee.get_gender_display(),
        'Marital Status': employee.get_maritalStatus_display(),
        'NIN': employee.nin,
        'Residential Address': employee.residentialAddress,
    }

    employment_fields = {
        'Date of First Appointment': employee.dateOfFirstAppointment,
        'Date of Present Appointment': employee.dateOfPresentAppointment,
        'Date of Confirmation': employee.dateOfConfirmation,
        'Cadre': employee.get_cadre_display(),
        'Current Grade Level': employee.currentGradeLevel,
        'Current Step': employee.currentStep,
        'Department': employee.department,
        'Division': employee.division,
        'State of Posting': employee.stateOfPosting,
        'Station': employee.station,
        'Present Appointment': employee.presentAppointment,
        'Last Promotion Date': employee.lastPromotionDate,
        'Retirement Date': employee.retirementDate,
    }

    financial_fields = {
        'Bank': employee.bank,
        'Account Type': employee.get_accountType_display(),
        'Account Number': employee.accountNumber,
        'PFA': employee.pfa,
        'PFA Number': employee.pfaNumber,
    }

    spouse_fields = {
        'Spouse Full Name': employee.spouse_fullName,
        'Spouse Occupation': employee.spouse_occupation,
        'Spouse Employer Name': employee.spouse_employerName,
        'Spouse Employment Period': employee.spouse_employmentPeriod,
    }

    next_of_kin = NextOfKin.objects.filter(employee=employee).first()
    nok_fields = {
        'NOK 1 Full Name': next_of_kin.nok1_fullName if next_of_kin else None,
        'NOK 1 Relationship': next_of_kin.get_nok1_relationship_display() if next_of_kin else None,
        'NOK 1 Address': next_of_kin.nok1_address if next_of_kin else None,
        'NOK 1 Phone Number': next_of_kin.nok1_phoneNumber if next_of_kin else None,
        'NOK 2 Full Name': next_of_kin.nok2_fullName if next_of_kin else None,
        'NOK 2 Relationship': next_of_kin.get_nok2_relationship_display() if next_of_kin else None,
        'NOK 2 Address': next_of_kin.nok2_address if next_of_kin else None,
        'NOK 2 Phone Number': next_of_kin.nok2_phoneNumber if next_of_kin else None,
    }

    education_fields = [
        {
            'Activity Type': education.get_activityType_display(),
            'Title': education.title,
            'Field of Study': education.fieldOfStudy,
            'Institution': education.institution,
            'Level': education.get_level_display(),
            'Start Date': education.startDate,
            'End Date': education.endDate,
            'Certificate Obtained': 'Yes' if education.certificateObtained else 'No',
        } for education in EducationAndTraining.objects.filter(employee=employee)
    ]

    previous_employment_fields = [
        {
            'Employer': employment.employer,
            'Organisation': employment.organisation,
            'Position': employment.position,
            'Start Date': employment.startDate,
            'End Date': employment.endDate,
        } for employment in PreviousEmployment.objects.filter(employee=employee)
    ]

    context = {
        'employee': employee,
        'personal_fields': personal_fields,
        'employment_fields': employment_fields,
        'financial_fields': financial_fields,
        'spouse_fields': spouse_fields,
        'nok_fields': nok_fields,
        'education_fields': education_fields,
        'previous_employment_fields': previous_employment_fields,
        'staff_audit': staff_audit,
        'discrepancies': discrepancies,
    }
    return render(request, 'hr_app/employee_detail.html', context)

@login_required
@user_passes_test(lambda u: is_authorized(u, ['DRUID_VIEWER', 'SUPER_ADMIN', 'DIRECTOR_GENERAL', 'HR_ADMIN', 'VERIFICATION_OFFICER']))
def employee_verification(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    discrepancies = Discrepancy.objects.filter(employee=employee, isResolved=False)

    if request.method == 'POST':
        form = EmployeeVerificationForm(request.POST, instance=employee)
        if form.is_valid():
            if discrepancies.count() == 0:
                verified_employee = form.save(commit=False)
                verified_employee.isVerified = True
                verified_employee.verifiedBy = request.user
                verified_employee.verificationDate = timezone.now()
                verified_employee.save()
                messages.success(request, f"Employee {employee.firstName} {employee.lastName} has been verified.")
                return redirect('employee_detail', employee_id=employee.id)
            else:
                messages.error(request, "All discrepancies must be resolved before final verification.")
    else:
        form = EmployeeVerificationForm(instance=employee)

    verification_status = {
        'Passport': employee.isPassportApproved,
        'Personal Information': employee.isPersonalInfoApproved,
        'Employment Information': employee.isEmploymentInfoApproved,
        'Education Information': employee.isEducationInfoApproved,
        'Financial Information': employee.isFinancialInfoApproved,
        'Next of Kin Information': employee.isNextOfKinInfoApproved,
        'Previous Employment': employee.isPreviousEmploymentApproved,
    }
    
    if employee.maritalStatus == 'M':
        verification_status['Spouse Information'] = employee.isSpouseInfoApproved

    all_sections_approved = all(verification_status.values())

    context = {
        'employee': employee,
        'discrepancies': discrepancies,
        'form': form,
        'verification_status': verification_status,
        'all_sections_approved': all_sections_approved,
    }
    return render(request, 'hr_app/employee_verification.html', context)


@login_required
@user_passes_test(lambda u: is_authorized(u, ['DRUID_VIEWER', 'SUPER_ADMIN', 'DIRECTOR_GENERAL', 'HR_ADMIN', 'VERIFICATION_OFFICER']))
def approve_section(request, employee_id):
    if request.method == 'POST':
        employee = get_object_or_404(Employee, id=employee_id)
        section = request.POST.get('section')
        is_approved = request.POST.get('is_approved') == 'true'

        if section == 'passport':
            employee.isPassportApproved = is_approved
        elif section == 'personal_info':
            employee.isPersonalInfoApproved = is_approved
        elif section == 'employment_info':
            employee.isEmploymentInfoApproved = is_approved
        elif section == 'education_info':
            employee.isEducationInfoApproved = is_approved
        elif section == 'financial_info':
            employee.isFinancialInfoApproved = is_approved
        elif section == 'next_of_kin_info':
            employee.isNextOfKinInfoApproved = is_approved
        elif section == 'spouse_info':
            employee.isSpouseInfoApproved = is_approved
        elif section == 'previous_employment':
            employee.isPreviousEmploymentApproved = is_approved
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid section'}, status=400)

        employee.save()
        return JsonResponse({'status': 'success', 'message': f'{section.replace("_", " ").title()} has been {"approved" if is_approved else "rejected"}.'})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

@login_required
@user_passes_test(lambda u: is_authorized(u, ['DRUID_VIEWER', 'SUPER_ADMIN', 'DIRECTOR_GENERAL', 'HR_ADMIN', 'VERIFICATION_OFFICER']))
def resolve_discrepancy(request, discrepancy_id):
    discrepancy = get_object_or_404(Discrepancy, id=discrepancy_id)
    employee = discrepancy.employee
    
    if request.method == 'POST':
        form = ResolveDiscrepancyForm(request.POST, instance=discrepancy, employee=employee, discrepancy=discrepancy)
        if form.is_valid():
            resolved_discrepancy = form.save(commit=False)
            resolved_discrepancy.isResolved = True
            resolved_discrepancy.resolvedBy = request.user
            resolved_discrepancy.resolutionDate = timezone.now()
            resolved_discrepancy.save()
            messages.success(request, "Discrepancy has been resolved.")
            return redirect('employee_verification', employee_id=employee.id)
    else:
        form = ResolveDiscrepancyForm(instance=discrepancy, employee=employee, discrepancy=discrepancy)
    
    context = {
        'discrepancy': discrepancy,
        'employee': employee,
        'form': form,
    }
    return render(request, 'hr_app/resolve_discrepancy.html', context)


@login_required
@user_passes_test(lambda u: is_authorized(u, ['DRUID_VIEWER', 'SUPER_ADMIN', 'HR_ADMIN']))
def employee_create(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Employee created successfully.")
            return redirect('manage_employees')
    else:
        form = EmployeeForm()

    context = {
        'form': form,
        'action': 'Create',
    }
    return render(request, 'hr_app/employee_form.html', context)


@login_required
@user_passes_test(lambda u: is_authorized(u, ['DRUID_VIEWER', 'SUPER_ADMIN', 'HR_ADMIN']))
def employee_edit(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, "Employee updated successfully.")
            return redirect('employee_detail', employee_id=employee.id)
    else:
        form = EmployeeForm(instance=employee)

    context = {
        'form': form,
        'action': 'Edit',
        'employee': employee,
    }
    return render(request, 'hr_app/employee_form.html', context)


@login_required
@user_passes_test(lambda u: is_authorized(u, ['DRUID_VIEWER']))
def employee_delete(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    if request.method == 'POST':
        employee.delete()
        messages.success(request, "Employee deleted successfully.")
        return redirect('manage_employees')

    context = {
        'object': employee,
        'object_name': f"Employee: {employee.firstName} {employee.lastName}",
    }
    return render(request, 'hr_app/confirm_delete.html', context)


@login_required
@user_passes_test(lambda u: is_authorized(u, ['DRUID_VIEWER', 'SUPER_ADMIN', 'HR_ADMIN']))
def manage_discrepancies(request):
    discrepancies = Discrepancy.objects.all()  # Get all discrepancies

    context = {
        'discrepancies': discrepancies,
    }
    return render(request, 'hr_app/manage_discrepancies.html', context)


@login_required
@user_passes_test(lambda u: is_authorized(u, ['DRUID_VIEWER', 'SUPER_ADMIN', 'HR_ADMIN']))
def resolve_discrepancy(request, discrepancy_id):
    discrepancy = get_object_or_404(Discrepancy, id=discrepancy_id)

    if request.method == 'POST':
        form = DiscrepancyResolveForm(request.POST, instance=discrepancy)
        if form.is_valid():
            form.save()
            discrepancy.isResolved = True
            discrepancy.resolvedBy = request.user
            discrepancy.save()
            messages.success(
                request, f"Discrepancy for {discrepancy.employee} has been resolved.")
            return redirect('manage_discrepancies')
    else:
        form = DiscrepancyResolveForm(instance=discrepancy)

    context = {
        'discrepancy': discrepancy,
        'form': form,
    }
    return render(request, 'hr_app/resolve_discrepancy.html', context)


@login_required
@user_passes_test(lambda u: is_authorized(u, ['DRUID_VIEWER', 'SUPER_ADMIN', 'HR_ADMIN']))
def manage_employees(request):
    query = request.GET.get('query')  # Get the search query

    employees = Employee.objects.filter(
        Q(stateOfPosting__in=request.user.userprofile.allowedStates.all()) |
        Q(department__in=request.user.userprofile.allowedDepartments.all())
    )

    if query:  # If a search query is provided
        employees = employees.filter(
            Q(firstName__icontains=query) |
            Q(ippisNumber__icontains=query) |
            Q(fileNumber__icontains=query)
            # Add other fields to search here (e.g., department, grade level)
        )

    paginator = Paginator(employees, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'employees': page_obj,
        'query': query,  # Pass the query to the template
    }
    return render(request, 'hr_app/manage_employees.html', context)

from django.apps import apps
from django.db.models import F

@login_required
def custom_report_builder(request):
    if request.method == 'POST':
        form = CustomReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.created_by = request.user
            report.save()
            return redirect('view_report', report_id=report.id)
    else:
        form = CustomReportForm()
    
    return render(request, 'hr_app/custom_report_builder.html', {'form': form})

@login_required
def get_model_fields(request):
    model_name = request.GET.get('model_name')
    form = CustomReportForm(data={'model_name': model_name})
    return JsonResponse({
        'fields': form.get_model_fields(model_name),
        'order_by': form.fields['order_by'].choices[1:],
    })

@login_required
def view_report(request, report_id):
    report = get_object_or_404(CustomReport, id=report_id)
    model = apps.get_model('hr_app', report.model_name)
    
    queryset = model.objects.all()
    if report.filters:
        queryset = queryset.filter(**report.filters)
    
    # Separate direct fields and related fields
    direct_fields = []
    related_fields = []
    annotate_dict = {}
    
    for field in report.fields:
        if '__' in field:
            related_fields.append(field)
            annotate_dict[field] = F(field)
        else:
            direct_fields.append(field)
    
    # Select direct fields and annotate related fields
    queryset = queryset.only(*direct_fields).annotate(**annotate_dict)
    
    if report.order_by:
        queryset = queryset.order_by(report.order_by)
    
    items_per_page = int(request.GET.get('items_per_page', 25))
    paginator = Paginator(queryset, items_per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Prepare data for display
    data = []
    for item in page_obj:
        row = {}
        for field in direct_fields:
            row[field] = getattr(item, field)
        for field in related_fields:
            row[field] = getattr(item, field)
        data.append(row)
    
    context = {
        'report': report,
        'page_obj': page_obj,
        'data': data,
        'items_per_page': items_per_page,
    }
    return render(request, 'hr_app/view_report.html', context)


@login_required
def add_report_filter(request, report_id):
    report = get_object_or_404(CustomReport, id=report_id)
    model_fields = [(f.name, f.verbose_name) for f in apps.get_model('hr_app', report.model_name)._meta.get_fields() if not f.is_relation]
    
    if request.method == 'POST':
        form = ReportFilterForm(request.POST, model_fields=model_fields)
        if form.is_valid():
            field = form.cleaned_data['field']
            operator = form.cleaned_data['operator']
            value = form.cleaned_data['value']
            
            filters = report.filters
            filters[f"{field}__{operator}"] = value
            report.filters = filters
            report.save()
            
            return redirect('view_report', report_id=report.id)
    else:
        form = ReportFilterForm(model_fields=model_fields)
    
    return render(request, 'hr_app/add_report_filter.html', {'form': form, 'report': report})


@login_required
def export_report_csv(request, report_id):
    report = get_object_or_404(CustomReport, id=report_id)
    model = apps.get_model('hr_app', report.model_name)
    
    queryset = model.objects.all()
    if report.filters:
        queryset = queryset.filter(**report.filters)
    
    # Separate direct fields and related fields
    direct_fields = []
    related_fields = []
    for field in report.fields:
        if '__' in field:
            related_fields.append(field)
        else:
            direct_fields.append(field)
    
    # Prepare response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{report.name}.csv"'
    
    writer = csv.writer(response)
    
    # Write headers
    headers = direct_fields + related_fields
    writer.writerow(headers)
    
    # Write data
    for item in queryset:
        row = []
        for field in direct_fields:
            row.append(getattr(item, field))
        for field in related_fields:
            row.append(getattr(item, field))
        writer.writerow(row)
    
    return response



@login_required
def saved_reports(request):
    reports = CustomReport.objects.filter(created_by=request.user)
    return render(request, 'hr_app/saved_reports.html', {'reports': reports})

@login_required
@user_passes_test(lambda u: is_authorized(u, ['DRUID_VIEWER']))
def system_settings(request):
    if request.method == 'POST':
        # Handle form submission for user roles and system features
        # Implement the logic to update user roles and toggle system features
        pass

    users = UserProfile.objects.all()
    # features = system_settings.objects.all()
    roles = UserProfile.USER_ROLES

    context = {
        'users': users,
        #    'features': features,
        'roles': roles,
    }
    return render(request, 'hr_app/system_settings.html', context)



@login_required
@user_passes_test(lambda u: is_authorized(u, ['DRUID_VIEWER','HR_DATA_SCREENING']))
def file_number_discrepancies(request):
    staff_audit_duplicates = StaffAuditEmployee.objects.values('fileNumber').annotate(
        count=Count('fileNumber')).filter(count__gt=1).order_by('fileNumber')
    
    employee_duplicates = Employee.objects.values('fileNumber').annotate(
        count=Count('fileNumber')).filter(count__gt=1).order_by('fileNumber')

    staff_paginator = Paginator(staff_audit_duplicates, 12)
    employee_paginator = Paginator(employee_duplicates, 12)

    page_number = request.GET.get('page')
    staff_page = staff_paginator.get_page(page_number)
    employee_page = employee_paginator.get_page(page_number)

    context = {
        'staff_audit_duplicates': staff_page,
        'employee_duplicates': employee_page,
    }
    return render(request, 'hr_app/file_number_discrepancies.html', context)


@login_required
@user_passes_test(lambda u: is_authorized(u, ['DRUID_VIEWER','HR_DATA_SCREENING']))
def file_number_detail(request, file_number):
    staff_audit_employees = StaffAuditEmployee.objects.filter(fileNumber=file_number)
    employees = Employee.objects.filter(fileNumber=file_number)

    context = {
        'file_number': file_number,
        'staff_audit_employees': staff_audit_employees,
        'employees': employees,
    }
    return render(request, 'hr_app/file_number_detail.html', context)

@login_required
@user_passes_test(lambda u: is_authorized(u, ['DRUID_VIEWER','HR_DATA_SCREENING']))
def edit_file_number(request, model, employee_id):
    if model == 'staff_audit':
        employee = get_object_or_404(StaffAuditEmployee, id=employee_id)
    else:
        employee = get_object_or_404(Employee, id=employee_id)

    if request.method == 'POST':
        form = FileNumberUpdateForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, f"File number for {employee.firstName} {employee.lastName} has been updated.")
            return redirect('file_number_detail', file_number=employee.fileNumber)
    else:
        form = FileNumberUpdateForm(instance=employee)

    context = {
        'form': form,
        'employee': employee,
        'model': model,
    }
    return render(request, 'hr_app/edit_file_number.html', context)


@login_required
def helpdesk(request):
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.created_by = request.user
            ticket.save()
            messages.success(request, "Ticket has been created successfully.")
            return redirect('helpdesk')
    else:
        form = TicketForm()

    tickets = Ticket.objects.filter(created_by=request.user)

    context = {
        'form': form,
        'tickets': tickets,
    }
    return render(request, 'hr_app/helpdesk.html', context)


@login_required
@user_passes_test(lambda u: is_authorized(u, ['HELPDESK']))
def manage_tickets(request):
    tickets = Ticket.objects.all()

    context = {
        'tickets': tickets,
    }
    return render(request, 'hr_app/manage_tickets.html', context)


@login_required
@user_passes_test(lambda u: is_authorized(u, ['HELPDESK']))
def resolve_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)

    if request.method == 'POST':
        ticket.is_resolved = True
        ticket.resolved_by = request.user
        ticket.save()
        messages.success(request, f"Ticket #{ticket.id} has been resolved.")
        return redirect('manage_tickets')

    context = {
        'ticket': ticket,
    }
    return render(request, 'hr_app/resolve_ticket.html', context)

# Helper functions


def get_verification_progress():
    total = Employee.objects.count()
    verified = Employee.objects.filter(isVerified=True).count()
    return (verified / total) * 100 if total > 0 else 0


def get_discrepancy_types():
    return Discrepancy.objects.values('discrepancyType').annotate(count=Count('discrepancyType'))


def get_system_health():
    # Implement logic to check system health (e.g., database connections, server status)
    return {'status': 'Good', 'last_backup': '2023-07-30 15:30:00'}


def get_duplicate_file_numbers():
    return StaffAuditEmployee.objects.values('fileNumber').annotate(
        count=Count('fileNumber')).filter(count__gt=1).count()

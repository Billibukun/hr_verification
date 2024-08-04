from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.HomepageView.as_view(), name='homepage'),
    # User URLs
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='user_detail'),
    path('users/add/', views.UserCreateView.as_view(), name='user_add'),
    path('users/<int:pk>/edit/', views.UserUpdateView.as_view(), name='user_edit'),
    path('users/<int:pk>/delete/', views.UserDeleteView.as_view(), name='user_delete'),
    # State URLs
    path('states/', views.StateListView.as_view(), name='state_list'),
    path('states/<int:pk>/', views.StateDetailView.as_view(), name='state_detail'),
    path('states/add/', views.StateCreateView.as_view(), name='state_add'),
    path('states/<int:pk>/edit/', views.StateUpdateView.as_view(), name='state_edit'),

    # LGA URLs
    path('lgas/', views.LGAListView.as_view(), name='lga_list'),
    path('lgas/<int:pk>/', views.LGADetailView.as_view(), name='lga_detail'),
    path('lgas/add/', views.LGACreateView.as_view(), name='lga_add'),
    path('lgas/<int:pk>/edit/', views.LGAUpdateView.as_view(), name='lga_edit'),
    
    path('divisions/', views.DivisionListView.as_view(), name='division_list'),
    path('divisions/<str:pk>/', views.DivisionDetailView.as_view(), name='division_detail'),
    path('divisions/add/', views.DivisionCreateView.as_view(), name='division_add'),
    path('divisions/<str:pk>/edit/', views.DivisionUpdateView.as_view(), name='division_edit'),
    path('divisions/<int:pk>/delete/', views.DivisionDeleteView.as_view(), name='division_delete'),

    path('departments/', views.DepartmentListView.as_view(), name='department_list'),
    path('departments/add/', views.DepartmentCreateView.as_view(), name='department_add'),
    path('departments/<int:pk>/', views.DepartmentDetailView.as_view(), name='department_detail'),
    path('departments/<int:pk>/edit/', views.DepartmentUpdateView.as_view(), name='department_edit'),
    path('departments/<int:pk>/delete/', views.DepartmentDeleteView.as_view(), name='department_delete'),

    path('gradelevels/', views.GradeLevelListView.as_view(), name='gradelevel_list'),
    path('gradelevels/add/', views.GradeLevelCreateView.as_view(), name='gradelevel_add'),
    path('gradelevels/<int:pk>/', views.GradeLevelDetailView.as_view(), name='gradelevel_detail'),
    path('gradelevels/<int:pk>/edit/', views.GradeLevelUpdateView.as_view(), name='gradelevel_edit'),
    path('gradelevels/<int:pk>/delete/', views.GradeLevelDeleteView.as_view(), name='gradelevel_delete'),

    path('officialappointments/', views.OfficialAppointmentListView.as_view(), name='officialappointment_list'),
    path('officialappointments/<str:pk>/', views.OfficialAppointmentDetailView.as_view(), name='officialappointment_detail'),
    path('officialappointments/add/', views.OfficialAppointmentCreateView.as_view(), name='officialappointment_add'),
    path('officialappointments/<str:pk>/edit/', views.OfficialAppointmentUpdateView.as_view(), name='officialappointment_edit'),
    path('officialappointments/<str:pk>/delete/', views.OfficialAppointmentDeleteView.as_view(), name='officialappointment_delete'),
    
    # employee urls
    path('user-login/', views.UserLoginView.as_view(), name='admin_login'),\
    path('accounts/profile/', views.profile, name='profile'),
    path('logout/', auth_views.LogoutView.as_view(next_page='admin_login'), name='logout'),
   
    # Employee summary (for initial review)
    path('employee/login/', views.employee_login, name='employee_login'),
    path('employee/<str:ippis_number>/summary/', views.employee_summary, name='employee_summary'),
    path('employee/<str:ippis_number>/dashboard/', views.employee_dashboard, name='employee_dashboard'),
    path('employee/<str:ippis_number>/update/personal/', views.update_personal_info, name='update_personal_info'),
    path('employee/<str:ippis_number>/update/employment/', views.update_employment_info, name='update_employment_info'),
    path('employee/<str:ippis_number>/update/education/', views.update_education_info, name='update_education_info'),
    path('employee/<str:ippis_number>/update/previous-employment/', views.update_previous_employment, name='update_previous_employment'),
    path('employee/<str:ippis_number>/update/next-of-kin/', views.update_next_of_kin, name='update_next_of_kin'),
    path('employee/<str:ippis_number>/update/financial/', views.update_financial_info, name='update_financial_info'),
    path('employee/<str:ippis_number>/update/spouse/', views.update_spouse_info, name='update_spouse_info'),
    path('employee/<str:ippis_number>/data-sheet/', views.employee_data_sheet, name='employee_data_sheet'),
    path('employee/<str:ippis_number>/generate-pdf/', views.generate_employee_pdf, name='generate_employee_pdf'),
    path('employee/data/', views.employee_data, name='employee_data'),
    # Generate and download PDF
    path('employee/generate-pdf/', views.generate_employee_pdf, name='generate_employee_pdf'),
    # Employee logout
    path('employee/logout/', views.employee_logout, name='employee_logout'),


    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('employees/', views.manage_employees, name='manage_employees'),
    path('employees/create/', views.employee_create, name='employee_create'),
    path('employees/<int:employee_id>/', views.employee_detail, name='employee_detail'),
    path('employees/<int:employee_id>/edit/', views.employee_edit, name='employee_edit'),
    path('employees/<int:employee_id>/delete/', views.employee_delete, name='employee_delete'),
    path('employees/search-verify/', views.search_verify_employees, name='search_verify_employees'),
    
    
    path('discrepancies/', views.manage_discrepancies, name='manage_discrepancies'),
    path('discrepancies/<int:discrepancy_id>/resolve/', views.resolve_discrepancy, name='resolve_discrepancy'),
    
    
    path('reports/custom/', views.custom_report_builder, name='custom_report_builder'),
    path('reports/get-model-fields/', views.get_model_fields, name='get_model_fields'),
    path('reports/view/<int:report_id>/', views.view_report, name='view_report'),
    path('reports/add-filter/<int:report_id>/', views.add_report_filter, name='add_report_filter'),
    path('export_report_csv/<int:report_id>/', views.export_report_csv, name='export_report_csv'),
    path('reports/saved/', views.saved_reports, name='saved_reports'),
    
    
    path('settings/', views.system_settings, name='system_settings'),
    
    
    path('employee/<int:employee_id>/', views.employee_detail, name='employee_detail'),
    path('employee/<int:employee_id>/verify/', views.employee_verification, name='employee_verification'),
    path('employee/<int:employee_id>/approve-section/', views.approve_section, name='approve_section'),
    path('discrepancy/<int:discrepancy_id>/resolve/', views.resolve_discrepancy, name='resolve_discrepancy'),
    
    
    path('file-number-discrepancies/', views.file_number_discrepancies, name='file_number_discrepancies'),
    path('file-number-detail/<str:file_number>/', views.file_number_detail, name='file_number_detail'),
    path('edit-file-number/<str:model>/<int:employee_id>/', views.edit_file_number, name='edit_file_number'),
   
   
    path('helpdesk/', views.helpdesk, name='helpdesk'),
    path('helpdesk/manage/', views.manage_tickets, name='manage_tickets'),
    path('helpdesk/<int:ticket_id>/resolve/', views.resolve_ticket, name='resolve_ticket'),

           
]
from django.contrib import admin
from .models import *
from import_export.admin import ImportExportModelAdmin

# Register your models here.


class UserProfileAdmin(ImportExportModelAdmin):
    list_display = ('user', 'department', 'role')
    list_filter = ('department', 'role')
    search_fields = ('user__username', 'user__email')
    pass


class ZoneAdmin(ImportExportModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')


class StateAdmin(ImportExportModelAdmin):
    list_display = ('name', 'code', 'zone')
    list_filter = ('name', 'zone')
    search_fields = ('name', 'code')


class LGAAdmin(ImportExportModelAdmin):
    list_display = ('name', 'state', 'code')
    list_filter = ('name', 'state')
    search_fields = ('name', 'code')
    

class DepartmentAdmin(ImportExportModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')
    
    
class DivisionAdmin(ImportExportModelAdmin):
    list_display = ('name', 'department', 'code')
    search_fields = ('name', 'department', 'code')
    

class GradeLevelAdmin(ImportExportModelAdmin):
    list_display = ('level', 'name', 'description',)
    search_fields = ('level', 'name', 'description',)

class OfficialAppointmentAdmin(ImportExportModelAdmin):
    list_display = ('code', 'name', 'gradeLevel', 'department')
    search_fields = ('code', 'name', 'gradeLevel', 'department')
    
    
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Zone, ZoneAdmin)
admin.site.register(State, StateAdmin)
admin.site.register(LGA, LGAAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(Division, DivisionAdmin)
admin.site.register(GradeLevel, GradeLevelAdmin)
admin.site.register(OfficialAppointment, OfficialAppointmentAdmin)

class StaffAuditEmployeeAdmin(ImportExportModelAdmin):
    list_display = ('surname', 'otherNames',)
    
admin.site.register(StaffAuditEmployee, StaffAuditEmployeeAdmin)
admin.site.register(Employee)
admin.site.register(EducationAndTraining)
admin.site.register(Discrepancy)


class PFAAdmin(ImportExportModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')
    
admin.site.register(PFA, PFAAdmin)

class BankAdmin(ImportExportModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')
admin.site.register(Bank, BankAdmin)

import os
from django.core.management.base import BaseCommand
from hr_app.models import *

class Command(BaseCommand):
    help = 'Populate database with initial data from CSV files (skipping duplicates and non-existent files)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting data population...'))

        self.populate_zones('data/zones.csv')
        self.populate_states('data/states.csv')
        self.populate_lgas('data/lgas.csv')
        self.populate_departments('data/departments.csv')
        self.populate_divisions('data/divisions.csv')
        self.populate_grade_levels('data/grade_levels.csv')
        self.populate_official_appointments('data/official_appointments.csv')
        self.populate_banks('data/banks.csv')
        self.populate_pfas('data/pfas.csv')

        self.stdout.write(self.style.SUCCESS('Data population completed!'))

    def populate_zones(self, filename):
        if not os.path.exists(filename):
            self.stdout.write(self.style.WARNING(f'File {filename} does not exist. Skipping zone population.'))
            return

        with open(filename, 'r') as f:
            next(f)  # Skip header row
            for line in f:
                name, code = line.strip().split(',')
                try:
                    # Check for duplicate Zone
                    if Zone.objects.filter(code=code).exists():
                        self.stdout.write(self.style.WARNING(f'Zone {name} ({code}) already exists. Skipping.'))
                        continue  # Skip to the next line
                    
                    Zone.objects.create(name=name, code=code)
                    self.stdout.write(self.style.SUCCESS(f'Zone {name} ({code}) populated.'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error populating Zone {name} ({code}): {e}'))

    def populate_states(self, filename):
        if not os.path.exists(filename):
            self.stdout.write(self.style.WARNING(f'File {filename} does not exist. Skipping state population.'))
            return

        with open(filename, 'r') as f:
            next(f)
            for line in f:
                name, code, zone_code = line.strip().split(',')
                try:
                    # Check for duplicate State
                    if State.objects.filter(code=code).exists():
                        self.stdout.write(self.style.WARNING(f'State {name} ({code}) already exists. Skipping.'))
                        continue 

                    zone = Zone.objects.get(code=zone_code)
                    State.objects.create(name=name, code=code, zone=zone)
                    self.stdout.write(self.style.SUCCESS(f'State {name} ({code}) populated.'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error populating State {name} ({code}): {e}'))

    def populate_lgas(self, filename):
        if not os.path.exists(filename):
            self.stdout.write(self.style.WARNING(f'File {filename} does not exist. Skipping LGA population.'))
            return

        with open(filename, 'r') as f:
            next(f)
            for line in f:
                name, code, state_code = line.strip().split(',')
                try:
                    # Check for duplicate LGA
                    if LGA.objects.filter(code=code).exists():
                        self.stdout.write(self.style.WARNING(f'LGA {name} ({code}) already exists. Skipping.'))
                        continue

                    state = State.objects.get(code=state_code)
                    LGA.objects.create(name=name, state=state, code=code)
                    self.stdout.write(self.style.SUCCESS(f'LGA {name} ({code}) populated.'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error populating LGA {name} ({code}): {e}'))

    def populate_departments(self, filename):
        if not os.path.exists(filename):
            self.stdout.write(self.style.WARNING(f'File {filename} does not exist. Skipping department population.'))
            return

        with open(filename, 'r') as f:
            next(f)
            for line in f:
                name, code = line.strip().split(',')
                try:
                    # Check for duplicate Department
                    if Department.objects.filter(code=code).exists():
                        self.stdout.write(self.style.WARNING(f'Department {name} ({code}) already exists. Skipping.'))
                        continue

                    Department.objects.create(name=name, code=code)
                    self.stdout.write(self.style.SUCCESS(f'Department {name} ({code}) populated.'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error populating Department {name} ({code}): {e}'))

    def populate_divisions(self, filename):
        if not os.path.exists(filename):
            self.stdout.write(self.style.WARNING(f'File {filename} does not exist. Skipping division population.'))
            return

        with open(filename, 'r') as f:
            next(f)
            for line in f:
                code, name, department_code = line.strip().split(',')
                try:
                    # Check for duplicate Division
                    if Division.objects.filter(code=code).exists():
                        self.stdout.write(self.style.WARNING(f'Division {name} ({code}) already exists. Skipping.'))
                        continue

                    department = Department.objects.get(code=department_code)
                    Division.objects.create(code=code, name=name, department=department)
                    self.stdout.write(self.style.SUCCESS(f'Division {name} ({code}) populated.'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error populating Division {name} ({code}): {e}'))

    def populate_grade_levels(self, filename):
        if not os.path.exists(filename):
            self.stdout.write(self.style.WARNING(f'File {filename} does not exist. Skipping grade level population.'))
            return

        with open(filename, 'r') as f:
            next(f)
            for line in f:
                level, name, description, per_diem, local_running, estacode, assumption_of_duty = line.strip().split(',')
                try:
                    # Check for duplicate Grade Level
                    if GradeLevel.objects.filter(level=int(level)).exists():
                        self.stdout.write(self.style.WARNING(f'Grade Level {name} ({level}) already exists. Skipping.'))
                        continue

                    GradeLevel.objects.create(
                        level=int(level),
                        name=name,
                        description=description,
                        perDiem=float(per_diem),
                        localRunning=float(local_running),
                        estacode=float(estacode),
                        assumptionOfDuty=float(assumption_of_duty)
                    )
                    self.stdout.write(self.style.SUCCESS(f'Grade Level {name} ({level}) populated.'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error populating Grade Level {name} ({level}): {e}'))

    def populate_official_appointments(self, filename):
        if not os.path.exists(filename):
            self.stdout.write(self.style.WARNING(f'File {filename} does not exist. Skipping official appointment population.'))
            return

        with open(filename, 'r') as f:
            next(f)
            for line in f:
                code, name, grade_level, cadre, department_code = line.strip().split(',')
                try:
                    # Check for duplicate Official Appointment
                    if OfficialAppointment.objects.filter(code=code).exists():
                        self.stdout.write(self.style.WARNING(f'Official Appointment {name} ({code}) already exists. Skipping.'))
                        continue

                    grade_level_obj = GradeLevel.objects.get(level=int(grade_level))
                    department_obj = Department.objects.get(code=department_code)
                    OfficialAppointment.objects.create(
                        code=code,
                        name=name,
                        gradeLevel=grade_level_obj,
                        cadre=cadre,
                        department=department_obj
                    )
                    self.stdout.write(self.style.SUCCESS(f'Official Appointment {name} ({code}) populated.'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error populating Official Appointment {name} ({code}): {e}'))
                    
    
    def populate_banks(self, filename):
        if not os.path.exists(filename):
            self.stdout.write(self.style.WARNING(f'File {filename} does not exist. Skipping bank population.'))
            return

        with open(filename, 'r') as f:
            next(f)
            for line in f:
                name, code = line.strip().split(',')
                try:
                    # Check for duplicate Bank
                    if Bank.objects.filter(code=code).exists():
                        self.stdout.write(self.style.WARNING(f'Bank {name} ({code}) already exists. Skipping.'))
                        continue

                    Bank.objects.create(name=name, code=code)
                    self.stdout.write(self.style.SUCCESS(f'Bank {name} ({code}) populated.'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error populating Bank {name} ({code}): {e}'))
                    
    def populate_pfas(self, filename):
        if not os.path.exists(filename):
            self.stdout.write(self.style.WARNING(f'File {filename} does not exist. Skipping pfa population.'))
            return
        
        with open(filename, 'r') as f:
            next(f)
            for line in f:
                name, code = line.strip().split(',')
                try:
                    # Check for duplicate PFA
                    if PFA.objects.filter(code=code).exists():
                        self.stdout.write(self.style.WARNING(f'PFA {name} ({code}) already exists. Skipping.'))
                        continue

                    PFA.objects.create(name=name, code=code)
                    self.stdout.write(self.style.SUCCESS(f'PFA {name} ({code}) populated.'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error populating PFA {name} ({code}): {e}'))
        
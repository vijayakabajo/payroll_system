from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date
import random


class Command(BaseCommand):
    help = 'Seed database with sample data: salary components, employees, and payslips.'

    def handle(self, *args, **options):
        self._seed_salary_components()
        self._seed_system_config()
        self._seed_employees()
        self._seed_payslips()
        self.stdout.write(self.style.SUCCESS('\n✅ All seed data created successfully!'))

    def _seed_salary_components(self):
        from apps.configs.models import SalaryComponent
        self.stdout.write('Seeding salary components...')

        components = [
            {'code': 'BASIC',   'name': 'Basic Amount',              'component_type': 'earning',   'calculation_type': 'manual',     'display_order': 1},
            {'code': 'HRA',     'name': 'House Rent Allowance',      'component_type': 'earning',   'calculation_type': 'percentage', 'percentage_value': 40, 'based_on': 'BASIC', 'display_order': 2},
            {'code': 'BONUS',   'name': 'Bonus',                     'component_type': 'earning',   'calculation_type': 'manual',     'display_order': 3},
            {'code': 'CA',      'name': 'Conveyance Allowance',      'component_type': 'earning',   'calculation_type': 'fixed',      'fixed_value': 1357, 'display_order': 4},
            {'code': 'CCA',     'name': 'City Compensatory Allowance','component_type': 'earning',   'calculation_type': 'fixed',      'fixed_value': 857, 'display_order': 5},
            {'code': 'MEDICAL', 'name': 'Medical Allowance',         'component_type': 'earning',   'calculation_type': 'fixed',      'fixed_value': 0, 'display_order': 6},
            {'code': 'MOBILE',  'name': 'Mobile & Internet',         'component_type': 'earning',   'calculation_type': 'fixed',      'fixed_value': 500, 'display_order': 7},
            {'code': 'WASHING', 'name': 'Washing Allowance',         'component_type': 'earning',   'calculation_type': 'fixed',      'fixed_value': 0, 'display_order': 8},
            {'code': 'SPECIAL', 'name': 'Special Allowance',         'component_type': 'earning',   'calculation_type': 'manual',     'display_order': 9},
            {'code': 'PF',      'name': 'Provident Fund',            'component_type': 'deduction', 'calculation_type': 'percentage', 'percentage_value': 12, 'based_on': 'BASIC', 'display_order': 10},
            {'code': 'ESI',     'name': 'ESI',                       'component_type': 'deduction', 'calculation_type': 'percentage', 'percentage_value': 0.75, 'display_order': 11},
            {'code': 'PT',      'name': 'Professional Tax',          'component_type': 'deduction', 'calculation_type': 'fixed',      'fixed_value': 200, 'display_order': 12},
            {'code': 'TDS',     'name': 'TDS',                       'component_type': 'deduction', 'calculation_type': 'manual',     'display_order': 13},
            {'code': 'LOAN',    'name': 'Loan Recovery',             'component_type': 'deduction', 'calculation_type': 'manual',     'display_order': 14},
            {'code': 'ADV_SAL', 'name': 'Advance Salary',            'component_type': 'deduction', 'calculation_type': 'manual',     'display_order': 15},
        ]

        basic_comp = None
        for comp_data in components:
            based_on_code = comp_data.pop('based_on', None)
            based_on_obj = None
            if based_on_code and basic_comp:
                based_on_obj = basic_comp

            obj, created = SalaryComponent.objects.update_or_create(
                code=comp_data['code'],
                defaults={
                    **comp_data,
                    'based_on_component': based_on_obj,
                }
            )
            if comp_data['code'] == 'BASIC':
                basic_comp = obj

            status = 'Created' if created else 'Updated'
            self.stdout.write(f'  {status}: {obj.code} — {obj.name}')

    def _seed_system_config(self):
        from apps.configs.models import SystemConfiguration
        self.stdout.write('Seeding system configuration...')

        configs = [
            {'key': 'company_name', 'value': 'Minu Marketing Pvt Ltd', 'description': 'Company name displayed on payslips'},
            {'key': 'company_tagline', 'value': 'Growing Together', 'description': 'Company tagline'},
            {'key': 'company_address', 'value': 'Ranchi, Jharkhand', 'description': 'Company address for payslips'},
            {'key': 'payslip_footer', 'value': 'This is a Computer Generated payslip. No signature is required.', 'description': 'Footer text on payslips'},
            {'key': 'esi_threshold', 'value': '21000', 'description': 'ESI applicable if gross <= this amount'},
            {'key': 'pf_ceiling', 'value': '15000', 'description': 'PF calculated on Basic up to this ceiling (0 = no ceiling)'},
        ]

        for cfg in configs:
            obj, created = SystemConfiguration.objects.update_or_create(
                key=cfg['key'],
                defaults=cfg,
            )
            status = 'Created' if created else 'Updated'
            self.stdout.write(f'  {status}: {obj.key}')

    def _seed_employees(self):
        from apps.employees.models import Employee
        self.stdout.write('Seeding sample employees...')

        employees = [
            {
                'employee_code': 'MMPL-001', 'full_name': 'Vijay Kumar Singh',
                'phone': '9876543210', 'email': 'vijay@minumarketing.com',
                'designation': 'Sales Manager', 'department': 'Sales', 'grade': 'M1',
                'bank_name': 'State Bank of India', 'account_number': '38271956482',
                'epf_ac_number': 'JHRAN/00123/456/0001234', 'pan_number': 'ABCDE1234F',
                'uan_number': '101381234567', 'esi_number': '6017123456',
                'joining_date': date(2022, 4, 1),
            },
            {
                'employee_code': 'MMPL-002', 'full_name': 'Priya Sharma',
                'phone': '9876543211', 'email': 'priya@minumarketing.com',
                'designation': 'Marketing Executive', 'department': 'Marketing', 'grade': 'F1',
                'bank_name': 'HDFC Bank', 'account_number': '50100287654321',
                'epf_ac_number': 'JHRAN/00123/456/0001235', 'pan_number': 'FGHIJ5678K',
                'uan_number': '101381234568', 'esi_number': '6017123457',
                'joining_date': date(2023, 1, 15),
            },
            {
                'employee_code': 'MMPL-003', 'full_name': 'Rajesh Patel',
                'phone': '9876543212', 'email': 'rajesh@minumarketing.com',
                'designation': 'Accountant', 'department': 'Finance', 'grade': 'F2',
                'bank_name': 'ICICI Bank', 'account_number': '123456789012',
                'epf_ac_number': 'JHRAN/00123/456/0001236', 'pan_number': 'KLMNO9012P',
                'uan_number': '101381234569', 'esi_number': '6017123458',
                'joining_date': date(2021, 8, 10),
            },
            {
                'employee_code': 'MMPL-004', 'full_name': 'Anita Kumari',
                'phone': '9876543213', 'email': 'anita@minumarketing.com',
                'designation': 'HR Executive', 'department': 'Human Resources', 'grade': 'F1',
                'bank_name': 'Axis Bank', 'account_number': '918010054321',
                'epf_ac_number': 'JHRAN/00123/456/0001237', 'pan_number': 'QRSTU3456V',
                'uan_number': '101381234570', 'esi_number': '6017123459',
                'joining_date': date(2023, 6, 1),
            },
            {
                'employee_code': 'MMPL-005', 'full_name': 'Suresh Yadav',
                'phone': '9876543214', 'email': 'suresh@minumarketing.com',
                'designation': 'Field Executive', 'department': 'Sales', 'grade': 'F3',
                'bank_name': 'Punjab National Bank', 'account_number': '0987654321098',
                'epf_ac_number': 'JHRAN/00123/456/0001238', 'pan_number': 'WXYZ67890A',
                'uan_number': '101381234571', 'esi_number': '6017123460',
                'joining_date': date(2024, 2, 15),
            },
        ]

        for emp_data in employees:
            obj, created = Employee.objects.update_or_create(
                employee_code=emp_data['employee_code'],
                defaults=emp_data,
            )
            status = 'Created' if created else 'Updated'
            self.stdout.write(f'  {status}: {obj.full_name} ({obj.employee_code})')

    def _seed_payslips(self):
        """Seed salary structures and generate sample payslips."""
        from apps.employees.models import Employee
        from apps.configs.models import SalaryComponent
        from apps.payroll.models import EmployeeSalaryStructure

        self.stdout.write('Seeding employee salary structures...')

        # Sample basic salaries per employee
        basic_salaries = {
            'MMPL-001': 15000,
            'MMPL-002': 12000,
            'MMPL-003': 18000,
            'MMPL-004': 10000,
            'MMPL-005': 8000,
        }

        for emp_code, basic in basic_salaries.items():
            try:
                emp = Employee.objects.get(employee_code=emp_code)
                basic_comp = SalaryComponent.objects.get(code='BASIC')
                EmployeeSalaryStructure.objects.update_or_create(
                    employee=emp, component=basic_comp,
                    defaults={'amount': basic}
                )
                self.stdout.write(f'  Set BASIC={basic} for {emp.full_name}')

                # Set BONUS = same as CA default
                try:
                    bonus_comp = SalaryComponent.objects.get(code='BONUS')
                    EmployeeSalaryStructure.objects.update_or_create(
                        employee=emp, component=bonus_comp,
                        defaults={'amount': 1357}
                    )
                except SalaryComponent.DoesNotExist:
                    pass

            except Employee.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'  Employee {emp_code} not found'))

        self.stdout.write(self.style.SUCCESS('  Salary structures seeded.'))
        self.stdout.write('  (Run payslip generation from the UI to create sample payslips)')

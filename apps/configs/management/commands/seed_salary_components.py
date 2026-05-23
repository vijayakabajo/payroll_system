"""
Management command to seed default salary components.
Idempotent — uses update_or_create so it can be run multiple times safely.

Usage:
    python manage.py seed_salary_components
"""
from django.core.management.base import BaseCommand
from apps.configs.models import SalaryComponent


class Command(BaseCommand):
    help = 'Seed default salary components for Minu Marketing Pvt Ltd payroll'

    def handle(self, *args, **options):
        self.stdout.write('Seeding salary components...')

        # --------------------------------------------------
        # EARNINGS
        # --------------------------------------------------
        basic, _ = SalaryComponent.objects.update_or_create(
            code='BASIC',
            defaults={
                'name': 'Basic Salary',
                'component_type': 'EARNING',
                'calculation_type': 'MANUAL',
                'display_order': 1,
                'is_active': True,
            },
        )

        SalaryComponent.objects.update_or_create(
            code='HRA',
            defaults={
                'name': 'House Rent Allowance',
                'component_type': 'EARNING',
                'calculation_type': 'PERCENTAGE',
                'percentage_value': 40.0000,
                'based_on_component': basic,
                'display_order': 2,
                'is_active': True,
            },
        )

        SalaryComponent.objects.update_or_create(
            code='BONUS',
            defaults={
                'name': 'Bonus',
                'component_type': 'EARNING',
                'calculation_type': 'MANUAL',
                'display_order': 3,
                'is_active': True,
            },
        )

        SalaryComponent.objects.update_or_create(
            code='CA',
            defaults={
                'name': 'Conveyance Allowance',
                'component_type': 'EARNING',
                'calculation_type': 'FIXED',
                'fixed_value': 1357.00,
                'display_order': 4,
                'is_active': True,
            },
        )

        SalaryComponent.objects.update_or_create(
            code='CCA',
            defaults={
                'name': 'City Compensatory Allowance',
                'component_type': 'EARNING',
                'calculation_type': 'FIXED',
                'fixed_value': 857.00,
                'display_order': 5,
                'is_active': True,
            },
        )

        SalaryComponent.objects.update_or_create(
            code='MEDICAL',
            defaults={
                'name': 'Medical Allowance',
                'component_type': 'EARNING',
                'calculation_type': 'FIXED',
                'fixed_value': 0.00,
                'display_order': 6,
                'is_active': True,
            },
        )

        SalaryComponent.objects.update_or_create(
            code='MOBILE',
            defaults={
                'name': 'Mobile Allowance',
                'component_type': 'EARNING',
                'calculation_type': 'FIXED',
                'fixed_value': 500.00,
                'display_order': 7,
                'is_active': True,
            },
        )

        SalaryComponent.objects.update_or_create(
            code='WASHING',
            defaults={
                'name': 'Washing Allowance',
                'component_type': 'EARNING',
                'calculation_type': 'FIXED',
                'fixed_value': 0.00,
                'display_order': 8,
                'is_active': True,
            },
        )

        SalaryComponent.objects.update_or_create(
            code='SPECIAL',
            defaults={
                'name': 'Special Allowance',
                'component_type': 'EARNING',
                'calculation_type': 'MANUAL',
                'display_order': 9,
                'is_active': True,
            },
        )

        # --------------------------------------------------
        # DEDUCTIONS
        # --------------------------------------------------
        SalaryComponent.objects.update_or_create(
            code='PF',
            defaults={
                'name': 'Provident Fund',
                'component_type': 'DEDUCTION',
                'calculation_type': 'PERCENTAGE',
                'percentage_value': 12.0000,
                'based_on_component': basic,
                'display_order': 10,
                'is_active': True,
            },
        )

        SalaryComponent.objects.update_or_create(
            code='ESI',
            defaults={
                'name': 'Employee State Insurance',
                'component_type': 'DEDUCTION',
                'calculation_type': 'PERCENTAGE',
                'percentage_value': 0.7500,
                'based_on_component': None,  # Calculated on gross
                'display_order': 11,
                'is_active': True,
            },
        )

        SalaryComponent.objects.update_or_create(
            code='PT',
            defaults={
                'name': 'Professional Tax',
                'component_type': 'DEDUCTION',
                'calculation_type': 'FIXED',
                'fixed_value': 200.00,
                'display_order': 12,
                'is_active': True,
            },
        )

        SalaryComponent.objects.update_or_create(
            code='TDS',
            defaults={
                'name': 'Tax Deducted at Source',
                'component_type': 'DEDUCTION',
                'calculation_type': 'MANUAL',
                'display_order': 13,
                'is_active': True,
            },
        )

        SalaryComponent.objects.update_or_create(
            code='LOAN',
            defaults={
                'name': 'Loan Recovery',
                'component_type': 'DEDUCTION',
                'calculation_type': 'MANUAL',
                'display_order': 14,
                'is_active': True,
            },
        )

        SalaryComponent.objects.update_or_create(
            code='ADV_SAL',
            defaults={
                'name': 'Advance Salary',
                'component_type': 'DEDUCTION',
                'calculation_type': 'MANUAL',
                'display_order': 15,
                'is_active': True,
            },
        )

        count = SalaryComponent.objects.filter(is_active=True).count()
        self.stdout.write(
            self.style.SUCCESS(f'Successfully seeded {count} salary components.')
        )

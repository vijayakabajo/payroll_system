"""
PayrollEngine — the core calculation engine for salary processing.

Resolves each salary component's amount based on configuration rules,
employee structure overrides, and proration logic.
"""
import logging
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional

from apps.configs.models import SalaryComponent
from apps.employees.models import Employee
from .models import EmployeeSalaryStructure, Payslip, PayslipItem

logger = logging.getLogger(__name__)

TWO_PLACES = Decimal('0.01')


@dataclass
class PayrollLineItem:
    """A single calculated line item."""
    component_code: str
    component_name: str
    component_type: str  # 'EARNING' or 'DEDUCTION'
    entitled_amount: Decimal = Decimal('0')
    earned_amount: Decimal = Decimal('0')
    display_order: int = 0


@dataclass
class PayrollResult:
    """Complete payroll calculation result."""
    employee: object = None
    month: str = ''
    year: int = 0
    paid_days: int = 30
    total_days: int = 30
    items: List[PayrollLineItem] = field(default_factory=list)
    gross_salary: Decimal = Decimal('0')
    gross_earned: Decimal = Decimal('0')
    total_deductions: Decimal = Decimal('0')
    net_salary: Decimal = Decimal('0')

    @property
    def earnings(self):
        return [i for i in self.items if i.component_type == 'EARNING']

    @property
    def deductions(self):
        return [i for i in self.items if i.component_type == 'DEDUCTION']


class PayrollEngine:
    """
    Core payroll calculation engine.

    Usage:
        engine = PayrollEngine()
        result = engine.calculate(employee, 'January', 2026, overrides={'BONUS': 5000})
        payslip = engine.generate_payslip(employee, 'January', 2026, overrides={'BONUS': 5000})
    """

    def calculate(
        self,
        employee: Employee,
        month: str,
        year: int,
        overrides: Optional[Dict[str, Decimal]] = None,
        paid_days: int = 30,
        total_days: int = 30,
        leave_data: Optional[dict] = None,
    ) -> PayrollResult:
        """
        Calculate payroll for an employee.

        Args:
            employee: Employee instance
            month: Month name (e.g. 'January')
            year: Year (e.g. 2026)
            overrides: dict of {component_code: amount} for manual overrides
            paid_days: Number of days actually paid
            total_days: Total working days in the month
            leave_data: dict with cl_taken, sl_taken, lwp_taken, ml_taken, pl_taken

        Returns:
            PayrollResult with all calculated items and totals
        """
        overrides = overrides or {}
        leave_data = leave_data or {}

        # 1. Get all active salary components
        components = SalaryComponent.objects.filter(
            is_active=True
        ).select_related('based_on_component').order_by('display_order')

        # 2. Get employee's salary structure (pre-configured amounts)
        structure_map = {}
        structures = EmployeeSalaryStructure.objects.filter(
            employee=employee
        ).select_related('component')
        for s in structures:
            structure_map[s.component.code] = s.amount

        # 3. Resolve amounts — first pass: earnings (to compute gross)
        resolved: Dict[str, Decimal] = {}
        items: List[PayrollLineItem] = []

        # Process earnings first
        earning_components = [c for c in components if c.component_type == 'EARNING']
        deduction_components = [c for c in components if c.component_type == 'DEDUCTION']

        for comp in earning_components:
            amount = self._resolve_amount(comp, overrides, structure_map, resolved)
            resolved[comp.code] = amount

            # Prorate: earned = entitled * paid_days / total_days
            if total_days > 0:
                earned = (amount * Decimal(paid_days) / Decimal(total_days)).quantize(TWO_PLACES, ROUND_HALF_UP)
            else:
                earned = Decimal('0')

            items.append(PayrollLineItem(
                component_code=comp.code,
                component_name=comp.name,
                component_type='EARNING',
                entitled_amount=amount,
                earned_amount=earned,
                display_order=comp.display_order,
            ))

        # Compute gross (sum of entitled earnings)
        gross_salary = sum(i.entitled_amount for i in items)
        gross_earned = sum(i.earned_amount for i in items)

        # Process deductions (NOT prorated)
        for comp in deduction_components:
            if comp.code in overrides:
                amount = Decimal(str(overrides[comp.code])).quantize(TWO_PLACES, ROUND_HALF_UP)
            elif comp.calculation_type == 'PERCENTAGE':
                if comp.based_on_component and comp.based_on_component.code in resolved:
                    base_amount = resolved[comp.based_on_component.code]
                else:
                    # ESI and similar: percentage of gross
                    base_amount = gross_salary
                pct = comp.percentage_value or Decimal('0')
                amount = (base_amount * pct / Decimal('100')).quantize(TWO_PLACES, ROUND_HALF_UP)
            elif comp.calculation_type == 'FIXED':
                amount = comp.fixed_value or Decimal('0')
            elif comp.code in structure_map:
                amount = structure_map[comp.code]
            else:
                amount = Decimal('0')

            resolved[comp.code] = amount

            items.append(PayrollLineItem(
                component_code=comp.code,
                component_name=comp.name,
                component_type='DEDUCTION',
                entitled_amount=amount,
                earned_amount=amount,  # Deductions are not prorated
                display_order=comp.display_order,
            ))

        total_deductions = sum(
            i.earned_amount for i in items if i.component_type == 'DEDUCTION'
        )
        net_salary = (gross_earned - total_deductions).quantize(TWO_PLACES, ROUND_HALF_UP)

        return PayrollResult(
            employee=employee,
            month=month,
            year=year,
            paid_days=paid_days,
            total_days=total_days,
            items=items,
            gross_salary=gross_salary.quantize(TWO_PLACES, ROUND_HALF_UP),
            gross_earned=gross_earned.quantize(TWO_PLACES, ROUND_HALF_UP),
            total_deductions=total_deductions.quantize(TWO_PLACES, ROUND_HALF_UP),
            net_salary=net_salary,
        )

    def _resolve_amount(
        self,
        component: SalaryComponent,
        overrides: Dict[str, Decimal],
        structure_map: Dict[str, Decimal],
        resolved: Dict[str, Decimal],
    ) -> Decimal:
        """
        Resolve the entitled amount for a single earning component.

        Priority:
        1. Manual override passed at generation time
        2. EmployeeSalaryStructure amount
        3. Component's built-in calculation (FIXED / PERCENTAGE / MANUAL→0)
        """
        code = component.code

        # 1. Override
        if code in overrides:
            return Decimal(str(overrides[code])).quantize(TWO_PLACES, ROUND_HALF_UP)

        # 2. Employee salary structure
        if code in structure_map:
            return structure_map[code].quantize(TWO_PLACES, ROUND_HALF_UP)

        # 3. Component calculation rules
        if component.calculation_type == 'FIXED':
            return (component.fixed_value or Decimal('0')).quantize(TWO_PLACES, ROUND_HALF_UP)

        if component.calculation_type == 'PERCENTAGE':
            if component.based_on_component:
                base_code = component.based_on_component.code
                base_amount = resolved.get(base_code, Decimal('0'))
            else:
                base_amount = Decimal('0')
            pct = component.percentage_value or Decimal('0')
            return (base_amount * pct / Decimal('100')).quantize(TWO_PLACES, ROUND_HALF_UP)

        # MANUAL with no override → 0
        return Decimal('0')

    def generate_payslip(
        self,
        employee: Employee,
        month: str,
        year: int,
        overrides: Optional[Dict[str, Decimal]] = None,
        paid_days: int = 30,
        total_days: int = 30,
        leave_data: Optional[dict] = None,
    ) -> Payslip:
        """
        Calculate payroll and create a Payslip + PayslipItem records.

        Raises:
            ValueError: If a payslip already exists for this employee/month/year.
        """
        # Check for duplicate
        if Payslip.objects.filter(employee=employee, month=month, year=year).exists():
            raise ValueError(
                f"Payslip already exists for {employee.full_name} — {month} {year}. "
                f"Delete the existing payslip first."
            )

        leave_data = leave_data or {}

        # Calculate
        result = self.calculate(
            employee=employee,
            month=month,
            year=year,
            overrides=overrides,
            paid_days=paid_days,
            total_days=total_days,
            leave_data=leave_data,
        )

        # Create Payslip
        payslip = Payslip.objects.create(
            employee=employee,
            month=month,
            year=year,
            paid_days=paid_days,
            total_days=total_days,
            cl_taken=leave_data.get('cl_taken', 0),
            sl_taken=leave_data.get('sl_taken', 0),
            lwp_taken=leave_data.get('lwp_taken', 0),
            ml_taken=leave_data.get('ml_taken', 0),
            pl_taken=leave_data.get('pl_taken', 0),
            gross_salary=result.gross_salary,
            gross_earned=result.gross_earned,
            total_deductions=result.total_deductions,
            net_salary=result.net_salary,
            generation_status='pending',
        )

        # Create PayslipItems (frozen snapshot)
        payslip_items = []
        for item in result.items:
            payslip_items.append(PayslipItem(
                payslip=payslip,
                component_name=item.component_name,
                component_code=item.component_code,
                component_type=item.component_type,
                entitled_amount=item.entitled_amount,
                earned_amount=item.earned_amount,
                display_order=item.display_order,
            ))
        PayslipItem.objects.bulk_create(payslip_items)

        logger.info(
            "Payslip generated: %s — %s %s | Net: %s",
            employee.full_name, month, year, result.net_salary,
        )

        return payslip

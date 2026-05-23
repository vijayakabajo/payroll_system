from django.db import models
from apps.core.models import TimeStampedModel


class EmployeeSalaryStructure(TimeStampedModel):
    """
    Stores the per-employee amount for each salary component.
    This is the employee's 'salary structure' — their entitled amounts.
    """

    employee = models.ForeignKey(
        'employees.Employee',
        on_delete=models.CASCADE,
        related_name='salary_structures',
    )
    component = models.ForeignKey(
        'configs.SalaryComponent',
        on_delete=models.CASCADE,
        related_name='employee_structures',
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Amount for this component (base amount before proration)",
    )

    class Meta:
        unique_together = ('employee', 'component')
        ordering = ['component__display_order']
        verbose_name = 'Employee Salary Structure'
        verbose_name_plural = 'Employee Salary Structures'

    def __str__(self):
        return f"{self.employee.full_name} — {self.component.code}: {self.amount}"


class Payslip(TimeStampedModel):
    """
    Generated payslip for an employee for a specific month/year.
    Stores computed totals and links to frozen PayslipItems.
    """

    GENERATION_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('generated', 'Generated'),
        ('failed', 'Failed'),
    ]

    WHATSAPP_STATUS_CHOICES = [
        ('not_sent', 'Not Sent'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    ]

    employee = models.ForeignKey(
        'employees.Employee',
        on_delete=models.CASCADE,
        related_name='payslips',
    )
    month = models.CharField(max_length=20)
    year = models.IntegerField()

    # Attendance / Leave
    paid_days = models.IntegerField(default=30)
    total_days = models.IntegerField(default=30)
    cl_taken = models.DecimalField(max_digits=4, decimal_places=1, default=0, verbose_name='CL Taken')
    sl_taken = models.DecimalField(max_digits=4, decimal_places=1, default=0, verbose_name='SL Taken')
    lwp_taken = models.DecimalField(max_digits=4, decimal_places=1, default=0, verbose_name='LWP Taken')
    ml_taken = models.DecimalField(max_digits=4, decimal_places=1, default=0, verbose_name='ML Taken')
    pl_taken = models.DecimalField(max_digits=4, decimal_places=1, default=0, verbose_name='PL Taken')

    # Computed totals
    gross_salary = models.DecimalField(max_digits=12, decimal_places=2, help_text="Sum of all entitled earnings")
    gross_earned = models.DecimalField(max_digits=12, decimal_places=2, help_text="Gross prorated by paid days")
    total_deductions = models.DecimalField(max_digits=12, decimal_places=2)
    net_salary = models.DecimalField(max_digits=12, decimal_places=2)

    # PDF & delivery
    pdf_file = models.FileField(upload_to='payslips/', blank=True)
    generation_status = models.CharField(
        max_length=10,
        choices=GENERATION_STATUS_CHOICES,
        default='pending',
    )
    whatsapp_status = models.CharField(
        max_length=10,
        choices=WHATSAPP_STATUS_CHOICES,
        default='not_sent',
    )

    class Meta:
        unique_together = ('employee', 'month', 'year')
        ordering = ['-year', '-created_at']
        verbose_name = 'Payslip'
        verbose_name_plural = 'Payslips'

    def __str__(self):
        return f"{self.employee.full_name} — {self.month} {self.year}"

    @property
    def period(self):
        return f"{self.month} {self.year}"

    @property
    def net_salary_in_words(self):
        from apps.core.utils import amount_in_words
        return amount_in_words(self.net_salary)


class PayslipItem(TimeStampedModel):
    """
    A frozen snapshot of a single salary component's calculated values
    at the time the payslip was generated. These never change once created.
    """

    COMPONENT_TYPE_CHOICES = [
        ('EARNING', 'Earning'),
        ('DEDUCTION', 'Deduction'),
    ]

    payslip = models.ForeignKey(
        Payslip,
        on_delete=models.CASCADE,
        related_name='items',
    )
    component_name = models.CharField(max_length=100)
    component_code = models.CharField(max_length=20)
    component_type = models.CharField(max_length=10, choices=COMPONENT_TYPE_CHOICES)
    entitled_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    earned_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    display_order = models.IntegerField(default=0)

    class Meta:
        ordering = ['display_order']
        verbose_name = 'Payslip Item'
        verbose_name_plural = 'Payslip Items'

    def __str__(self):
        return f"{self.payslip} — {self.component_name}: {self.earned_amount}"

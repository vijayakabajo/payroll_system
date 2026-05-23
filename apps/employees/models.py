from django.db import models
from apps.core.models import TimeStampedModel


class Employee(TimeStampedModel):
    """
    Core employee record for Minu Marketing Pvt Ltd.
    Contains all fields visible on the payslip reference.
    """

    employee_code  = models.CharField(unique=True, max_length=20, help_text="e.g. MMPL-001")
    full_name      = models.CharField(max_length=200)
    phone          = models.CharField(max_length=15)
    email          = models.EmailField(blank=True)
    designation    = models.CharField(max_length=100)
    department     = models.CharField(max_length=100)
    grade          = models.CharField(max_length=20, blank=True, help_text="e.g. F1, M1")

    # Bank & statutory details (shown on payslip)
    bank_name      = models.CharField(max_length=100, blank=True)
    account_number = models.CharField(max_length=30, blank=True)
    epf_ac_number  = models.CharField(max_length=50, blank=True, verbose_name="EPF A/C Number")
    pan_number     = models.CharField(max_length=10, blank=True, verbose_name="PAN Number")
    uan_number     = models.CharField(max_length=20, blank=True, verbose_name="UAN Number")
    esi_number     = models.CharField(max_length=20, blank=True, verbose_name="ESIC Number")

    joining_date   = models.DateField()
    is_active      = models.BooleanField(default=True)

    class Meta:
        ordering = ['full_name']
        verbose_name = 'Employee'
        verbose_name_plural = 'Employees'

    def __str__(self):
        return f"{self.full_name} ({self.employee_code})"

    @property
    def initials(self):
        parts = self.full_name.strip().split()
        if len(parts) >= 2:
            return f"{parts[0][0]}{parts[-1][0]}".upper()
        return self.full_name[:2].upper()

    @property
    def masked_account(self):
        if self.account_number and len(self.account_number) > 4:
            return 'X' * (len(self.account_number) - 4) + self.account_number[-4:]
        return self.account_number

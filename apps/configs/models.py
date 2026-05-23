from django.db import models
from apps.core.models import TimeStampedModel


class SalaryComponent(TimeStampedModel):
    """
    Defines a single salary component (earning or deduction)
    with its calculation rules.
    """

    COMPONENT_TYPE_CHOICES = [
        ('EARNING', 'Earning'),
        ('DEDUCTION', 'Deduction'),
    ]

    CALCULATION_TYPE_CHOICES = [
        ('FIXED', 'Fixed Amount'),
        ('PERCENTAGE', 'Percentage'),
        ('MANUAL', 'Manual Entry'),
    ]

    code = models.CharField(
        unique=True,
        max_length=20,
        help_text="Unique component code, e.g. BASIC, HRA, PF",
    )
    name = models.CharField(max_length=100, help_text="Display name for the component")
    component_type = models.CharField(
        max_length=10,
        choices=COMPONENT_TYPE_CHOICES,
        help_text="Whether this is an earning or deduction",
    )
    calculation_type = models.CharField(
        max_length=10,
        choices=CALCULATION_TYPE_CHOICES,
        help_text="How this component's amount is calculated",
    )
    percentage_value = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Percentage value (e.g. 40.0000 for 40%)",
    )
    fixed_value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Fixed amount in INR",
    )
    based_on_component = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='dependent_components',
        help_text="Component this percentage is calculated on (e.g. HRA based on BASIC)",
    )
    is_active = models.BooleanField(default=True)
    display_order = models.IntegerField(
        default=0,
        help_text="Order in which this component appears on payslips",
    )

    class Meta:
        ordering = ['display_order', 'code']
        verbose_name = 'Salary Component'
        verbose_name_plural = 'Salary Components'

    def __str__(self):
        return f"{self.name} ({self.code})"

    @property
    def calculation_description(self):
        """Human-readable description of how the amount is calculated."""
        if self.calculation_type == 'FIXED':
            from apps.core.utils import format_indian_currency
            return f"{format_indian_currency(self.fixed_value)} Fixed"
        elif self.calculation_type == 'PERCENTAGE':
            pct = self.percentage_value or 0
            # Remove trailing zeros for display
            pct_display = f"{pct:g}" if pct == int(pct) else f"{pct}"
            base = self.based_on_component.name if self.based_on_component else 'Gross'
            return f"{pct_display}% of {base}"
        return 'Manual Entry'


class SystemConfiguration(TimeStampedModel):
    """
    Key-value store for system-wide configuration settings.
    """

    key = models.CharField(
        unique=True,
        max_length=100,
        help_text="Unique setting key, e.g. company_name",
    )
    value = models.TextField(help_text="Setting value")
    description = models.CharField(
        max_length=255,
        blank=True,
        help_text="Human-readable description of what this setting does",
    )

    class Meta:
        ordering = ['key']
        verbose_name = 'System Configuration'
        verbose_name_plural = 'System Configurations'

    def __str__(self):
        return f"{self.key} = {self.value[:50]}"

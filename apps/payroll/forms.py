from django import forms
from decimal import Decimal
from apps.employees.models import Employee
from apps.configs.models import SalaryComponent
from apps.core.utils import get_month_choices
from .models import Payslip


class PayslipGenerateForm(forms.Form):
    """
    Form for generating a payslip. Includes static fields plus
    dynamically-generated override fields for each active salary component.
    """

    employee = forms.ModelChoiceField(
        queryset=Employee.objects.filter(is_active=True).order_by('full_name'),
        empty_label='— Select Employee —',
    )
    month = forms.ChoiceField(choices=get_month_choices)
    year = forms.IntegerField(min_value=2020, max_value=2099)
    paid_days = forms.IntegerField(min_value=0, max_value=31, initial=30)
    total_days = forms.IntegerField(min_value=1, max_value=31, initial=30)

    # Leave fields
    cl_taken = forms.DecimalField(
        max_digits=4, decimal_places=1, initial=0, required=False,
        label='CL Taken',
    )
    sl_taken = forms.DecimalField(
        max_digits=4, decimal_places=1, initial=0, required=False,
        label='SL Taken',
    )
    lwp_taken = forms.DecimalField(
        max_digits=4, decimal_places=1, initial=0, required=False,
        label='LWP Taken',
    )
    ml_taken = forms.DecimalField(
        max_digits=4, decimal_places=1, initial=0, required=False,
        label='ML Taken',
    )
    pl_taken = forms.DecimalField(
        max_digits=4, decimal_places=1, initial=0, required=False,
        label='PL Taken',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Apply form-control class to all static fields
        for field_name, field_obj in self.fields.items():
            field_obj.widget.attrs['class'] = 'form-control'

        # Dynamically add override fields for each active salary component
        components = SalaryComponent.objects.filter(is_active=True).order_by('display_order')
        for comp in components:
            field_key = f'override_{comp.code}'
            self.fields[field_key] = forms.DecimalField(
                max_digits=12,
                decimal_places=2,
                required=False,
                label=comp.name,
                help_text=comp.calculation_description,
                widget=forms.NumberInput(attrs={
                    'class': 'form-control',
                    'placeholder': f'{comp.calculation_description}',
                    'step': '0.01',
                    'data_component_code': comp.code,
                    'data_component_type': comp.component_type,
                }),
            )

    def get_overrides(self):
        """Extract override values from cleaned data."""
        overrides = {}
        for key, value in self.cleaned_data.items():
            if key.startswith('override_') and value is not None and value != '':
                code = key.replace('override_', '')
                overrides[code] = Decimal(str(value))
        return overrides

    def get_leave_data(self):
        """Extract leave data from cleaned data."""
        return {
            'cl_taken': self.cleaned_data.get('cl_taken') or 0,
            'sl_taken': self.cleaned_data.get('sl_taken') or 0,
            'lwp_taken': self.cleaned_data.get('lwp_taken') or 0,
            'ml_taken': self.cleaned_data.get('ml_taken') or 0,
            'pl_taken': self.cleaned_data.get('pl_taken') or 0,
        }

    def clean(self):
        cleaned = super().clean()
        employee = cleaned.get('employee')
        month = cleaned.get('month')
        year = cleaned.get('year')

        if employee and month and year:
            if Payslip.objects.filter(employee=employee, month=month, year=year).exists():
                raise forms.ValidationError(
                    f"A payslip already exists for {employee.full_name} — {month} {year}. "
                    f"Delete it first to regenerate."
                )
        return cleaned

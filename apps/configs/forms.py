from django import forms
from .models import SalaryComponent, SystemConfiguration


class SalaryComponentForm(forms.ModelForm):
    """Form for creating/editing salary components."""

    class Meta:
        model = SalaryComponent
        fields = [
            'code', 'name', 'component_type', 'calculation_type',
            'percentage_value', 'fixed_value', 'based_on_component',
            'display_order', 'is_active',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                continue
            field.widget.attrs['class'] = 'form-control'

        # Only show active earning components as base options
        self.fields['based_on_component'].queryset = SalaryComponent.objects.filter(
            is_active=True,
            component_type='EARNING',
        ).exclude(pk=self.instance.pk if self.instance.pk else None)
        self.fields['based_on_component'].empty_label = '— None (Gross) —'
        self.fields['percentage_value'].required = False
        self.fields['fixed_value'].required = False
        self.fields['based_on_component'].required = False

    def clean(self):
        cleaned = super().clean()
        calc_type = cleaned.get('calculation_type')
        if calc_type == 'PERCENTAGE':
            if not cleaned.get('percentage_value'):
                self.add_error('percentage_value', 'Percentage value is required for percentage-type components.')
        elif calc_type == 'FIXED':
            if cleaned.get('fixed_value') is None:
                self.add_error('fixed_value', 'Fixed value is required for fixed-type components.')
        return cleaned


class SystemConfigForm(forms.ModelForm):
    """Form for system configuration entries."""

    class Meta:
        model = SystemConfiguration
        fields = ['key', 'value', 'description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

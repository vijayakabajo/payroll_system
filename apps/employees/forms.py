from django import forms
from .models import Employee


class EmployeeForm(forms.ModelForm):

    class Meta:
        model = Employee
        fields = [
            'employee_code', 'full_name', 'phone', 'email',
            'designation', 'department', 'grade', 'joining_date',
            'bank_name', 'account_number', 'epf_ac_number',
            'pan_number', 'uan_number', 'esi_number',
            'is_active',
        ]
        widgets = {
            'joining_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply consistent styling to all fields
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-checkbox'})
            else:
                field.widget.attrs.update({
                    'class': 'form-control',
                    'placeholder': field.label,
                })
        # Make certain fields not required
        optional = ['email', 'grade', 'bank_name', 'account_number',
                    'epf_ac_number', 'pan_number', 'uan_number', 'esi_number']
        for f in optional:
            self.fields[f].required = False

    def clean_employee_code(self):
        code = self.cleaned_data.get('employee_code', '').strip().upper()
        qs = Employee.objects.filter(employee_code=code)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("An employee with this code already exists.")
        return code

    def clean_pan_number(self):
        pan = self.cleaned_data.get('pan_number', '').strip().upper()
        if pan and len(pan) != 10:
            raise forms.ValidationError("PAN must be exactly 10 characters.")
        return pan

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        digits = ''.join(filter(str.isdigit, phone))
        if len(digits) < 10:
            raise forms.ValidationError("Enter a valid 10-digit phone number.")
        return phone

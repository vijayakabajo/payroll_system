import datetime

from django import forms


MONTH_CHOICES = [
    ('January', 'January'),
    ('February', 'February'),
    ('March', 'March'),
    ('April', 'April'),
    ('May', 'May'),
    ('June', 'June'),
    ('July', 'July'),
    ('August', 'August'),
    ('September', 'September'),
    ('October', 'October'),
    ('November', 'November'),
    ('December', 'December'),
]


class BulkUploadForm(forms.Form):
    """
    Upload form: accepts an .xlsx file, the target month, and year.
    """

    file = forms.FileField(
        label='Excel File',
        help_text='Upload a .xlsx file with payroll data.',
        widget=forms.ClearableFileInput(attrs={
            'accept': '.xlsx',
            'class': 'form-control',
            'id': 'file-input',
        }),
    )

    month = forms.ChoiceField(
        choices=MONTH_CHOICES,
        label='Month',
        initial=lambda: MONTH_CHOICES[datetime.date.today().month - 1][0],
    )

    year = forms.IntegerField(
        label='Year',
        initial=lambda: datetime.date.today().year,
        min_value=2020,
        max_value=2099,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name != 'file':  # file already has class set
                field.widget.attrs.setdefault('class', 'form-control')

    def clean_file(self):
        f = self.cleaned_data.get('file')
        if f:
            if not f.name.endswith('.xlsx'):
                raise forms.ValidationError('Only .xlsx files are supported.')
            # 10 MB limit
            if f.size > 10 * 1024 * 1024:
                raise forms.ValidationError('File size must be under 10 MB.')
        return f

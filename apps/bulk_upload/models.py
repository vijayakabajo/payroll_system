from django.db import models
from apps.core.models import TimeStampedModel


class BulkUpload(TimeStampedModel):
    """
    Tracks a single bulk-upload job: the uploaded Excel file,
    target month/year, progress counters, and the final status.
    """

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('partial', 'Partial'),
        ('failed', 'Failed'),
    ]

    file = models.FileField(upload_to='uploads/')
    month = models.CharField(max_length=20)
    year = models.IntegerField()
    total_rows = models.IntegerField(default=0)
    success_count = models.IntegerField(default=0)
    failed_count = models.IntegerField(default=0)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
    )
    error_report = models.FileField(
        upload_to='uploads/errors/',
        blank=True,
        null=True,
    )
    uploaded_by = models.CharField(max_length=100, default='admin')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Bulk Upload'
        verbose_name_plural = 'Bulk Uploads'

    def __str__(self):
        return f"Upload #{self.pk} — {self.month}/{self.year} ({self.get_status_display()})"

    @property
    def progress_percent(self):
        """Return processing progress as a percentage (0–100)."""
        if self.total_rows == 0:
            return 0
        processed = self.success_count + self.failed_count
        return round((processed / self.total_rows) * 100)

    @property
    def filename(self):
        """Return just the file name (no directory path)."""
        if self.file:
            import os
            return os.path.basename(self.file.name)
        return ''


class BulkUploadRow(TimeStampedModel):
    """
    One row from the uploaded Excel sheet.
    Stores raw data, processing status, and a link to the
    generated Payslip on success.
    """

    ROW_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    ]

    bulk_upload = models.ForeignKey(
        BulkUpload,
        on_delete=models.CASCADE,
        related_name='rows',
    )
    row_number = models.IntegerField()
    employee_code = models.CharField(max_length=20)
    raw_data = models.JSONField()
    status = models.CharField(
        max_length=20,
        choices=ROW_STATUS_CHOICES,
        default='pending',
    )
    error_message = models.TextField(blank=True)
    payslip = models.ForeignKey(
        'payroll.Payslip',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ['row_number']
        verbose_name = 'Upload Row'
        verbose_name_plural = 'Upload Rows'

    def __str__(self):
        return f"Row {self.row_number} — {self.employee_code} ({self.get_status_display()})"

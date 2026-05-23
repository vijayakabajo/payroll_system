from django.db import models
from apps.core.models import TimeStampedModel


class WhatsAppMessage(TimeStampedModel):
    """Mock WhatsApp message record — placeholder for future real API integration."""

    STATUS_CHOICES = [
        ('not_sent', 'Not Sent'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    ]

    payslip     = models.ForeignKey('payroll.Payslip', on_delete=models.CASCADE, related_name='whatsapp_messages')
    phone       = models.CharField(max_length=15)
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_sent')
    is_mock     = models.BooleanField(default=True)
    sent_at     = models.DateTimeField(null=True, blank=True)
    error_log   = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'WhatsApp Message'
        verbose_name_plural = 'WhatsApp Messages'

    def __str__(self):
        return f"WhatsApp → {self.phone} ({self.status})"

import logging
from django.utils import timezone

logger = logging.getLogger(__name__)


class WhatsAppSender:
    """
    Mock WhatsApp sender — logs to console and creates DB records.
    Replace with real Meta Cloud API integration when ready.
    """

    def send_payslip(self, phone, payslip):
        """Send payslip via WhatsApp (MOCK — just logs and records)."""
        from .models import WhatsAppMessage

        logger.info(
            f"[MOCK WhatsApp] Would send payslip for {payslip.employee.full_name} "
            f"({payslip.month} {payslip.year}) to {phone}"
        )

        msg = WhatsAppMessage.objects.create(
            payslip=payslip,
            phone=phone,
            status='sent',
            is_mock=True,
            sent_at=timezone.now(),
        )

        # Update payslip whatsapp_status
        payslip.whatsapp_status = 'sent'
        payslip.save(update_fields=['whatsapp_status'])

        return True

    def send_bulk(self, payslips):
        """Send payslips to all employees (MOCK)."""
        results = []
        for ps in payslips:
            try:
                success = self.send_payslip(ps.employee.phone, ps)
                results.append({'payslip': ps, 'success': success})
            except Exception as e:
                results.append({'payslip': ps, 'success': False, 'error': str(e)})
        return results

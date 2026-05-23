import logging
from pathlib import Path
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone

logger = logging.getLogger(__name__)

class PayslipPDFGenerator:
    """Generates PDF payslips using WeasyPrint."""

    def generate(self, payslip):
        """
        Renders the payslip HTML template and converts it to PDF.
        Saves the file to the media directory and updates the payslip record.
        """
        try:
            # 1. Fetch data
            employee = payslip.employee
            items = payslip.items.all()
            
            earnings = [item for item in items if item.component_type == 'EARNING']
            deductions = [item for item in items if item.component_type == 'DEDUCTION']
            
            # Fetch company config (mocked via SystemConfiguration or fallback)
            from apps.configs.models import SystemConfiguration
            company_name = SystemConfiguration.objects.filter(key='company_name').values_list('value', flat=True).first() or 'Minu Marketing Pvt Ltd'
            company_tagline = SystemConfiguration.objects.filter(key='company_tagline').values_list('value', flat=True).first() or 'Growing Together'
            company_address = SystemConfiguration.objects.filter(key='company_address').values_list('value', flat=True).first() or 'Ranchi, Jharkhand'
            
            # Use absolute file path for the logo for WeasyPrint
            logo_path = Path(settings.BASE_DIR) / 'static' / 'images' / 'logo.png'
            logo_url = f"file:///{logo_path.as_posix()}" if logo_path.exists() else ""
            
            from apps.core.utils import amount_in_words
            
            context = {
                'payslip': payslip,
                'employee': employee,
                'earnings': earnings,
                'deductions': deductions,
                'company_name': company_name,
                'company_tagline': company_tagline,
                'company_address': company_address,
                'logo_url': logo_url,
                'net_amount_words': amount_in_words(payslip.net_salary),
                'now': timezone.now(),
            }
            
            # 2. Render HTML
            html_string = render_to_string('pdf/payslip_template.html', context)
            
            # 3. Define output path
            output_dir = Path(settings.MEDIA_ROOT) / 'payslips' / str(payslip.year) / payslip.month.lower()
            output_dir.mkdir(parents=True, exist_ok=True)
            
            filename = f"{employee.employee_code}_{payslip.month}_{payslip.year}.pdf"
            file_path = output_dir / filename
            
            # 4. Generate PDF via xhtml2pdf
            from xhtml2pdf import pisa
            
            with open(file_path, "wb") as pdf_file:
                pisa_status = pisa.CreatePDF(
                    html_string, dest=pdf_file, link_callback=None
                )
                
            if pisa_status.err:
                raise Exception("Failed to generate PDF with xhtml2pdf")
            
            # 5. Update Payslip record
            rel_path = f"payslips/{payslip.year}/{payslip.month.lower()}/{filename}"
            payslip.pdf_file.name = rel_path
            payslip.generation_status = 'generated'
            payslip.save(update_fields=['pdf_file', 'generation_status'])
            
            logger.info(f"PDF generated successfully for {employee.employee_code} ({payslip.month} {payslip.year})")
            return str(file_path)
            
        except Exception as e:
            logger.exception(f"Failed to generate PDF for Payslip {payslip.id}")
            payslip.generation_status = 'failed'
            payslip.save(update_fields=['generation_status'])
            return None

import logging
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse, FileResponse, Http404
from django.core.paginator import Paginator
from django.db.models import Q

from apps.employees.models import Employee
from apps.configs.models import SalaryComponent
from apps.core.utils import get_month_choices, format_indian_currency
from .models import Payslip, PayslipItem, EmployeeSalaryStructure
from .forms import PayslipGenerateForm
from .engine import PayrollEngine

logger = logging.getLogger(__name__)


def generate_payslip(request):
    """Generate a new payslip for an employee."""
    if request.method == 'POST':
        form = PayslipGenerateForm(request.POST)
        if form.is_valid():
            try:
                engine = PayrollEngine()
                payslip = engine.generate_payslip(
                    employee=form.cleaned_data['employee'],
                    month=form.cleaned_data['month'],
                    year=form.cleaned_data['year'],
                    overrides=form.get_overrides(),
                    paid_days=form.cleaned_data['paid_days'],
                    total_days=form.cleaned_data['total_days'],
                    leave_data=form.get_leave_data(),
                )

                # Try to generate PDF
                try:
                    from apps.pdf_generator.generator import PayslipPDFGenerator
                    generator = PayslipPDFGenerator()
                    pdf_path = generator.generate(payslip)
                    payslip.refresh_from_db(fields=['generation_status', 'pdf_file'])
                    if not pdf_path:
                        messages.warning(
                            request,
                            'Payslip record was created, but PDF generation failed. Check the server logs.',
                        )
                except Exception as e:
                    logger.warning("PDF generation failed: %s", str(e))
                    payslip.generation_status = 'failed'
                    payslip.save(update_fields=['generation_status'])

                messages.success(
                    request,
                    f'Payslip generated for {payslip.employee.full_name} — {payslip.month} {payslip.year}'
                )
                return redirect('payroll:detail', pk=payslip.pk)

            except ValueError as e:
                messages.error(request, str(e))
            except Exception as e:
                logger.exception("Payslip generation error")
                messages.error(request, f'Error generating payslip: {str(e)}')
    else:
        import datetime
        now = datetime.datetime.now()
        form = PayslipGenerateForm(initial={
            'month': now.strftime('%B'),
            'year': now.year,
            'paid_days': 30,
            'total_days': 30,
        })

    # Group override fields by component type for template
    earning_fields = []
    deduction_fields = []
    components = SalaryComponent.objects.filter(is_active=True).order_by('display_order')
    for comp in components:
        field_key = f'override_{comp.code}'
        if field_key in form.fields:
            field_info = {
                'field': form[field_key],
                'component': comp,
            }
            if comp.component_type == 'EARNING':
                earning_fields.append(field_info)
            else:
                deduction_fields.append(field_info)

    context = {
        'form': form,
        'earning_fields': earning_fields,
        'deduction_fields': deduction_fields,
        'month_choices': get_month_choices(),
    }
    return render(request, 'payroll/generate.html', context)


def payslip_history(request):
    """List all payslips with search and filtering."""
    payslips = Payslip.objects.select_related('employee').all()

    # Filters
    query = request.GET.get('q', '').strip()
    month_filter = request.GET.get('month', '')
    year_filter = request.GET.get('year', '')
    status_filter = request.GET.get('status', '')

    if query:
        payslips = payslips.filter(
            Q(employee__full_name__icontains=query) |
            Q(employee__employee_code__icontains=query)
        )
    if month_filter:
        payslips = payslips.filter(month=month_filter)
    if year_filter:
        try:
            payslips = payslips.filter(year=int(year_filter))
        except ValueError:
            pass
    if status_filter:
        payslips = payslips.filter(generation_status=status_filter)

    # Pagination
    paginator = Paginator(payslips, 25)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'payslips': page_obj,
        'query': query,
        'month_filter': month_filter,
        'year_filter': year_filter,
        'status_filter': status_filter,
        'month_choices': get_month_choices(),
        'total_count': paginator.count,
    }

    if request.headers.get('HX-Request'):
        return render(request, 'payroll/partials/_payslip_table.html', context)
    return render(request, 'payroll/history.html', context)


def payslip_detail(request, pk):
    """Show detailed payslip view."""
    payslip = get_object_or_404(
        Payslip.objects.select_related('employee'),
        pk=pk,
    )
    items = payslip.items.all().order_by('display_order')
    earnings = [i for i in items if i.component_type == 'EARNING']
    deductions = [i for i in items if i.component_type == 'DEDUCTION']

    context = {
        'payslip': payslip,
        'earnings': earnings,
        'deductions': deductions,
        'employee': payslip.employee,
    }
    return render(request, 'payroll/detail.html', context)


def payslip_download(request, pk):
    """Serve the payslip PDF file."""
    payslip = get_object_or_404(Payslip, pk=pk)

    if not payslip.pdf_file:
        # Try to generate on the fly
        try:
            from apps.pdf_generator.generator import PayslipPDFGenerator
            generator = PayslipPDFGenerator()
            generator.generate(payslip)
            payslip.refresh_from_db()
        except Exception as e:
            logger.warning("PDF generation failed on download: %s", str(e))

    if not payslip.pdf_file:
        raise Http404("PDF file not available. Please try regenerating the payslip.")

    try:
        response = FileResponse(
            payslip.pdf_file.open('rb'),
            content_type='application/pdf',
        )
        filename = f"{payslip.employee.employee_code}_{payslip.month}_{payslip.year}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    except FileNotFoundError:
        raise Http404("PDF file not found on disk.")


def payslip_delete(request, pk):
    """Delete a payslip."""
    if request.method != 'POST':
        return HttpResponse(status=405)

    payslip = get_object_or_404(Payslip, pk=pk)
    employee_name = payslip.employee.full_name
    period = payslip.period

    # Delete PDF file if it exists
    if payslip.pdf_file:
        try:
            payslip.pdf_file.delete(save=False)
        except Exception:
            pass

    payslip.delete()
    messages.success(request, f'Payslip for {employee_name} — {period} has been deleted.')
    return redirect('payroll:history')


def employee_salary_structure(request, employee_pk):
    """HTMX view: load/save an employee's salary structure."""
    employee = get_object_or_404(Employee, pk=employee_pk)
    components = SalaryComponent.objects.filter(is_active=True).order_by('display_order')

    if request.method == 'POST':
        updated = 0
        for comp in components:
            field_name = f'amount_{comp.code}'
            amount_str = request.POST.get(field_name, '').strip()
            if amount_str:
                try:
                    amount = Decimal(amount_str)
                    EmployeeSalaryStructure.objects.update_or_create(
                        employee=employee,
                        component=comp,
                        defaults={'amount': amount},
                    )
                    updated += 1
                except Exception:
                    pass
            else:
                # If empty, remove existing structure entry
                EmployeeSalaryStructure.objects.filter(
                    employee=employee,
                    component=comp,
                ).delete()

        messages.success(request, f'Salary structure updated for {employee.full_name} ({updated} components).')
        if request.headers.get('HX-Request'):
            pass  # Will re-render the partial

    # Build structure data
    existing = {
        s.component_id: s.amount
        for s in EmployeeSalaryStructure.objects.filter(employee=employee)
    }
    structure_items = []
    for comp in components:
        structure_items.append({
            'component': comp,
            'amount': existing.get(comp.pk, ''),
        })

    context = {
        'employee': employee,
        'structure_items': structure_items,
    }
    return render(request, 'payroll/salary_structure.html', context)

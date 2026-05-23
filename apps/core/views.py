from django.shortcuts import render, redirect
from django.conf import settings


# ==========================================
# PIN AUTH VIEWS
# ==========================================

def pin_login(request):
    """PIN authentication view."""
    if request.session.get('pin_authenticated'):
        return redirect('core:dashboard')

    error = None
    if request.method == 'POST':
        pin = request.POST.get('pin', '').strip()
        if pin == settings.APP_PIN:
            request.session['pin_authenticated'] = True
            request.session.set_expiry(settings.SESSION_COOKIE_AGE)
            next_url = request.GET.get('next', 'core:dashboard')
            return redirect(next_url)
        else:
            error = 'Incorrect PIN. Please try again.'

    return render(request, 'pin_login.html', {'error': error})


def pin_logout(request):
    """Clear PIN session and redirect to login."""
    request.session.flush()
    return redirect('login')


def dashboard_redirect(request):
    """Root URL redirects to dashboard."""
    return redirect('core:dashboard')


# ==========================================
# DASHBOARD VIEWS
# ==========================================

def dashboard_view(request):
    """Main dashboard with lazy-loaded HTMX widgets."""
    return render(request, 'dashboard/index.html')


def dashboard_stats_widget(request):
    """HTMX widget: stats cards."""
    try:
        from apps.employees.models import Employee
        from apps.payroll.models import Payslip
        from apps.bulk_upload.models import BulkUpload
        from django.utils import timezone

        now = timezone.now()
        current_month = now.strftime('%B')
        current_year = now.year

        total_employees = Employee.objects.filter(is_active=True).count()
        payslips_this_month = Payslip.objects.filter(
            month=current_month, year=current_year,
            generation_status='generated'
        ).count()

        context = {
            'total_employees': total_employees,
            'payslips_this_month': payslips_this_month,
            'pending_payslips': max(0, total_employees - payslips_this_month),
            'total_uploads': BulkUpload.objects.count(),
            'current_month': current_month,
            'current_year': current_year,
        }
    except Exception:
        context = {
            'total_employees': 0, 'payslips_this_month': 0,
            'pending_payslips': 0, 'total_uploads': 0,
            'current_month': '', 'current_year': '',
        }
    return render(request, 'dashboard/partials/_stats.html', context)


def recent_uploads_widget(request):
    """HTMX widget: recent bulk uploads."""
    try:
        from apps.bulk_upload.models import BulkUpload
        uploads = BulkUpload.objects.order_by('-created_at')[:5]
    except Exception:
        uploads = []
    return render(request, 'dashboard/partials/_recent_uploads.html', {'uploads': uploads})


def activity_widget(request):
    """HTMX widget: recent payslip activity."""
    try:
        from apps.payroll.models import Payslip
        recent = Payslip.objects.select_related('employee').order_by('-created_at')[:10]
    except Exception:
        recent = []
    return render(request, 'dashboard/partials/_activity.html', {'payslips': recent})

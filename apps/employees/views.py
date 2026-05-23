from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import Employee
from .forms import EmployeeForm


def employee_list(request):
    """Paginated employee list with live search."""
    query = request.GET.get('q', '').strip()
    dept  = request.GET.get('dept', '').strip()
    status = request.GET.get('status', 'active')

    qs = Employee.objects.all()

    if status == 'active':
        qs = qs.filter(is_active=True)
    elif status == 'inactive':
        qs = qs.filter(is_active=False)

    if query:
        qs = qs.filter(
            Q(full_name__icontains=query) |
            Q(employee_code__icontains=query) |
            Q(designation__icontains=query) |
            Q(phone__icontains=query)
        )
    if dept:
        qs = qs.filter(department__icontains=dept)

    departments = Employee.objects.values_list('department', flat=True).distinct().order_by('department')

    paginator = Paginator(qs, 20)
    page = paginator.get_page(request.GET.get('page', 1))

    context = {
        'page_obj': page,
        'query': query,
        'dept': dept,
        'status': status,
        'departments': departments,
        'total_count': qs.count(),
    }

    # HTMX partial for live search
    if request.headers.get('HX-Request'):
        return render(request, 'employees/partials/_employee_table.html', context)

    return render(request, 'employees/list.html', context)


def employee_create(request):
    """Create a new employee."""
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            emp = form.save()
            messages.success(request, f"Employee '{emp.full_name}' added successfully.")
            if request.POST.get('save_and_add'):
                return redirect('employees:create')
            return redirect('employees:list')
    else:
        form = EmployeeForm()

    return render(request, 'employees/create.html', {'form': form, 'title': 'Add Employee'})


def employee_edit(request, pk):
    """Edit an existing employee."""
    employee = get_object_or_404(Employee, pk=pk)

    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            emp = form.save()
            messages.success(request, f"Employee '{emp.full_name}' updated successfully.")
            return redirect('employees:detail', pk=emp.pk)
    else:
        form = EmployeeForm(instance=employee)

    return render(request, 'employees/edit.html', {
        'form': form,
        'employee': employee,
        'title': f'Edit — {employee.full_name}',
    })


def employee_detail(request, pk):
    """Employee profile with payslip history."""
    employee = get_object_or_404(Employee, pk=pk)

    try:
        from apps.payroll.models import Payslip
        payslips = Payslip.objects.filter(employee=employee).order_by('-year', '-created_at')[:12]
    except Exception:
        payslips = []

    return render(request, 'employees/detail.html', {
        'employee': employee,
        'payslips': payslips,
    })


@require_POST
def employee_toggle_status(request, pk):
    """Soft delete / reactivate — toggle is_active."""
    employee = get_object_or_404(Employee, pk=pk)
    employee.is_active = not employee.is_active
    employee.save(update_fields=['is_active'])
    action = "activated" if employee.is_active else "deactivated"
    messages.success(request, f"Employee '{employee.full_name}' {action}.")

    if request.headers.get('HX-Request'):
        # Return updated row
        return render(request, 'employees/partials/_employee_row.html', {'emp': employee})

    return redirect('employees:list')


def employee_delete(request, pk):
    """Hard delete with confirmation (GET=confirm page, POST=delete)."""
    employee = get_object_or_404(Employee, pk=pk)

    if request.method == 'POST':
        name = employee.full_name
        employee.delete()
        messages.success(request, f"Employee '{name}' permanently deleted.")
        return redirect('employees:list')

    return render(request, 'employees/confirm_delete.html', {'employee': employee})

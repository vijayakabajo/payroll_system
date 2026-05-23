from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from .models import SalaryComponent, SystemConfiguration
from .forms import SalaryComponentForm, SystemConfigForm


def salary_components_list(request):
    """List all salary components grouped by type."""
    earnings = SalaryComponent.objects.filter(
        component_type='EARNING', is_active=True
    ).order_by('display_order')
    deductions = SalaryComponent.objects.filter(
        component_type='DEDUCTION', is_active=True
    ).order_by('display_order')

    context = {
        'earnings': earnings,
        'deductions': deductions,
        'total_count': earnings.count() + deductions.count(),
    }

    if request.headers.get('HX-Request'):
        return render(request, 'configs/salary_components.html', context)
    return render(request, 'configs/salary_components.html', context)


def salary_component_create(request):
    """Create a new salary component."""
    if request.method == 'POST':
        form = SalaryComponentForm(request.POST)
        if form.is_valid():
            component = form.save()
            messages.success(request, f'Component "{component.name}" created successfully.')
            return redirect('configs:salary_components')
    else:
        form = SalaryComponentForm()

    context = {
        'form': form,
        'title': 'Add Salary Component',
        'is_edit': False,
    }
    return render(request, 'configs/salary_component_form.html', context)


def salary_component_edit(request, pk):
    """Edit an existing salary component."""
    component = get_object_or_404(SalaryComponent, pk=pk)

    if request.method == 'POST':
        form = SalaryComponentForm(request.POST, instance=component)
        if form.is_valid():
            form.save()
            messages.success(request, f'Component "{component.name}" updated successfully.')
            return redirect('configs:salary_components')
    else:
        form = SalaryComponentForm(instance=component)

    context = {
        'form': form,
        'component': component,
        'title': f'Edit {component.name}',
        'is_edit': True,
    }
    return render(request, 'configs/salary_component_form.html', context)


def salary_component_delete(request, pk):
    """Soft-delete a salary component (set is_active=False)."""
    if request.method != 'POST':
        return HttpResponse(status=405)

    component = get_object_or_404(SalaryComponent, pk=pk)
    component.is_active = False
    component.save(update_fields=['is_active'])
    messages.success(request, f'Component "{component.name}" has been deactivated.')
    return redirect('configs:salary_components')


def system_settings(request):
    """List and update system configuration key-value pairs."""
    if request.method == 'POST':
        # Inline update: keys are submitted as config_{pk}
        configs = SystemConfiguration.objects.all()
        updated = 0
        for config in configs:
            field_name = f'config_{config.pk}'
            new_value = request.POST.get(field_name)
            if new_value is not None and new_value != config.value:
                config.value = new_value
                config.save(update_fields=['value', 'updated_at'])
                updated += 1
        if updated:
            messages.success(request, f'{updated} setting(s) updated successfully.')
        else:
            messages.info(request, 'No changes detected.')
        return redirect('configs:system_settings')

    configs = SystemConfiguration.objects.all()
    context = {
        'configs': configs,
    }
    return render(request, 'configs/system_settings.html', context)

from django.urls import path
from . import views

app_name = 'payroll'

urlpatterns = [
    path('generate/', views.generate_payslip, name='generate'),
    path('history/', views.payslip_history, name='history'),
    path('<int:pk>/', views.payslip_detail, name='detail'),
    path('<int:pk>/download/', views.payslip_download, name='download'),
    path('<int:pk>/delete/', views.payslip_delete, name='delete'),
    path('salary-structure/<int:employee_pk>/', views.employee_salary_structure, name='salary_structure'),
]

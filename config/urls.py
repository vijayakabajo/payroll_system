from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.core import views as core_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', core_views.pin_login, name='login'),
    path('logout/', core_views.pin_logout, name='logout'),
    path('', core_views.dashboard_redirect, name='home'),
    path('dashboard/', include('apps.core.urls', namespace='core')),
    path('employees/', include('apps.employees.urls', namespace='employees')),
    path('configs/', include('apps.configs.urls', namespace='configs')),
    path('payroll/', include('apps.payroll.urls', namespace='payroll')),
    path('bulk-upload/', include('apps.bulk_upload.urls', namespace='bulk_upload')),
    path('whatsapp/', include('apps.whatsapp.urls', namespace='whatsapp')),
    path('api/employees/', include('apps.employees.api_urls', namespace='api_employees')),
    path('api/payroll/', include('apps.payroll.api_urls', namespace='api_payroll')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

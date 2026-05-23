from django.urls import path
from django.http import HttpResponse

app_name = 'configs'

def placeholder_view(request):
    return HttpResponse("Placeholder")

urlpatterns = [
    path('salary-components/', placeholder_view, name='salary_components'),
    path('system-settings/', placeholder_view, name='system_settings'),
]

from django.urls import path
from django.http import HttpResponse

app_name = 'payroll'

def placeholder_view(request):
    return HttpResponse("Placeholder")

urlpatterns = [
    path('generate/', placeholder_view, name='generate'),
    path('history/', placeholder_view, name='history'),
    path('download/<int:pk>/', placeholder_view, name='download'),
]

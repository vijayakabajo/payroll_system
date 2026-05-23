from django.urls import path
from django.http import HttpResponse

app_name = 'bulk_upload'

def placeholder_view(request):
    return HttpResponse("Placeholder")

urlpatterns = [
    path('upload/', placeholder_view, name='upload'),
    path('history/', placeholder_view, name='history'),
]

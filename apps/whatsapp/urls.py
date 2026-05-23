from django.urls import path
from django.http import HttpResponse

app_name = 'whatsapp'

def placeholder_view(request):
    return HttpResponse("WhatsApp module — placeholder. Real API integration coming soon.")

urlpatterns = [
    path('', placeholder_view, name='index'),
]

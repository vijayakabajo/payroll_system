from django.urls import path
from . import views

app_name = 'bulk_upload'

urlpatterns = [
    path('upload/', views.upload_view, name='upload'),
    path('upload/<int:pk>/progress/', views.upload_progress, name='progress'),
    path('history/', views.upload_history, name='history'),
    path('template/', views.download_template, name='download_template'),
    path('<int:pk>/errors/', views.download_error_report, name='error_report'),
]

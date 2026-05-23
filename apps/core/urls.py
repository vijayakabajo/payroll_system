from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('widgets/stats/', views.dashboard_stats_widget, name='dashboard_stats'),
    path('widgets/recent-uploads/', views.recent_uploads_widget, name='recent_uploads_widget'),
    path('widgets/activity/', views.activity_widget, name='activity_widget'),
]

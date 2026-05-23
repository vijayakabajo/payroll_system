from django.urls import path
from . import views

app_name = 'configs'

urlpatterns = [
    path('salary-components/', views.salary_components_list, name='salary_components'),
    path('salary-components/add/', views.salary_component_create, name='salary_component_create'),
    path('salary-components/<int:pk>/edit/', views.salary_component_edit, name='salary_component_edit'),
    path('salary-components/<int:pk>/delete/', views.salary_component_delete, name='salary_component_delete'),
    path('system-settings/', views.system_settings, name='system_settings'),
]

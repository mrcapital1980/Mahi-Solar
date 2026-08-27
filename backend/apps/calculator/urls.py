from django.urls import path
from . import views

urlpatterns = [
    path('', views.calculator_view, name='calculator'),
    path('calculate/', views.calculate_solar, name='calculate_solar'),
    path('save-lead/', views.save_calculator_lead, name='save_calculator_lead'),
]

from django.urls import path
from . import views

urlpatterns = [
    path('contact/', views.contact_view, name='contact'),
    path('site-visit/', views.site_visit_view, name='site_visit'),
    path('contacts-list/', views.list_contacts, name='list_contacts'),
    path('contacts-toggle/<int:lead_id>/', views.toggle_contact_resolve, name='toggle_contact_resolve'),
    path('site-visits-list/', views.list_site_visits, name='list_site_visits'),
    path('site-visits-toggle/<int:lead_id>/', views.toggle_site_visit_confirm, name='toggle_site_visit_confirm'),
    path('calculator-list/', views.list_calculator_leads, name='list_calculator_leads'),
]

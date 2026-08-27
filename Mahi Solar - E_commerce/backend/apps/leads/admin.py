from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import ContactLead, SiteVisitLead, CalculatorLead


@admin.register(ContactLead)
class ContactLeadAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'subject', 'is_resolved', 'created_at']
    list_filter = ['is_resolved', 'created_at']
    search_fields = ['name', 'email', 'phone']
    list_editable = ['is_resolved']


@admin.register(SiteVisitLead)
class SiteVisitLeadAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'city', 'preferred_date', 'preferred_slot', 'is_confirmed', 'created_at']
    list_filter = ['is_confirmed', 'preferred_slot', 'city', 'created_at']
    search_fields = ['name', 'email', 'phone']
    list_editable = ['is_confirmed']


@admin.register(CalculatorLead)
class CalculatorLeadAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'monthly_bill', 'recommended_kw', 'estimated_cost', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'email', 'phone']

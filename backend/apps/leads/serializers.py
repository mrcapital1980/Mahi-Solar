from rest_framework import serializers
from .models import ContactLead, SiteVisitLead, CalculatorLead


class ContactLeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactLead
        fields = ['id', 'name', 'email', 'phone', 'subject', 'message']
        read_only_fields = ['id']


class SiteVisitLeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteVisitLead
        fields = [
            'id', 'name', 'email', 'phone', 'address', 'city',
            'preferred_date', 'preferred_slot', 'notes',
        ]
        read_only_fields = ['id', 'is_confirmed']


class CalculatorLeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = CalculatorLead
        fields = [
            'id', 'name', 'email', 'phone', 'monthly_bill', 'units_per_month',
            'recommended_kw', 'estimated_cost', 'roof_area',
        ]
        read_only_fields = ['id']

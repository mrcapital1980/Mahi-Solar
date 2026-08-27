from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from .models import ContactLead, SiteVisitLead, CalculatorLead
from .serializers import ContactLeadSerializer, SiteVisitLeadSerializer, CalculatorLeadSerializer


class ContactLeadViewSet(viewsets.ModelViewSet):
    queryset = ContactLead.objects.all()
    serializer_class = ContactLeadSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        lead = serializer.save()
        try:
            send_mail(
                subject=f"New Contact: {lead.subject}",
                message=f"Name: {lead.name}\nEmail: {lead.email}\nPhone: {lead.phone}\n\nMessage:\n{lead.message}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.CONTACT_EMAIL],
                fail_silently=True,
            )
            send_mail(
                subject="Thank you for contacting Mahi Solar!",
                message=f"Dear {lead.name},\n\nWe have received your enquiry and will get back to you within 24 hours.\n\nBest regards,\nMahi Solar Team\nSurat, Gujarat",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[lead.email],
                fail_silently=True,
            )
        except Exception:
            pass
        return Response({
            'success': True,
            'id': lead.id,
            'message': 'Thank you! We will contact you within 24 hours.',
        }, status=201)


class SiteVisitLeadViewSet(viewsets.ModelViewSet):
    queryset = SiteVisitLead.objects.all()
    serializer_class = SiteVisitLeadSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        lead = serializer.save()
        try:
            owner = (
                f"New Site Visit Request Details:\n"
                f"Name: {lead.name}\nPhone: {lead.phone}\nEmail: {lead.email}\n"
                f"Address: {lead.address}, {lead.city}\n"
                f"Preferred Date: {lead.preferred_date}\nSlot: {lead.preferred_slot}\nNotes: {lead.notes}"
            )
            send_mail(
                subject=f'New Site Visit Request from {lead.name}',
                message=owner,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.CONTACT_EMAIL],
                fail_silently=True,
            )
            customer = (
                f"Dear {lead.name},\n\nWe have received your site visit request for {lead.preferred_date} "
                f"during the {lead.preferred_slot}. Our team will contact you shortly.\n\nBest regards,\nMahi Solar Team"
            )
            send_mail(
                subject='Site Visit Request Received - Mahi Solar',
                message=customer,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[lead.email],
                fail_silently=True,
            )
        except Exception:
            pass
        return Response({
            'success': True,
            'id': lead.id,
            'message': 'Site visit request submitted!',
        }, status=201)


class CalculatorAPIViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return CalculatorLead.objects.all()

    @action(detail=False, methods=['post'])
    def calculate(self, request):
        data = request.data
        monthly_bill = float(data.get('monthly_bill') or data.get('monthly_bill', 0))
        units = float(data.get('units') or data.get('units', 0))
        if units == 0 and monthly_bill > 0:
            units = monthly_bill / 8
        recommended_kw = max(round(units / 120, 2), 1.0)
        estimated_cost = recommended_kw * 60000
        if recommended_kw <= 2:
            subsidy = 18000 * min(recommended_kw, 2)
        else:
            subsidy = 36000 + (recommended_kw - 2) * 9000
        final_cost = max(estimated_cost - subsidy, 0)
        roof_area = recommended_kw * 100
        annual_savings = units * 12 * 8
        roi_years = round(final_cost / annual_savings, 1) if annual_savings > 0 else 0
        lead_payload = {
            'name': data.get('name', ''),
            'email': data.get('email', ''),
            'phone': data.get('phone', ''),
            'monthly_bill': monthly_bill,
            'units_per_month': units,
            'recommended_kw': recommended_kw,
            'estimated_cost': estimated_cost,
            'roof_area': roof_area,
        }
        if lead_payload['name'] and lead_payload['email']:
            CalculatorLead.objects.create(**lead_payload)
        return Response({
            'success': True,
            'recommended_kw': recommended_kw,
            'estimated_cost': round(estimated_cost),
            'subsidy': round(subsidy),
            'final_cost': round(final_cost),
            'roof_area': round(roof_area),
            'annual_savings': round(annual_savings),
            'roi_years': roi_years,
            'monthly_savings': round(annual_savings / 12),
        })

    @action(detail=False, methods=['post'])
    def save_lead(self, request):
        data = request.data
        lead = CalculatorLead.objects.create(
            name=data.get('name', ''),
            email=data.get('email', ''),
            phone=data.get('phone', ''),
            monthly_bill=data.get('monthly_bill', 0),
            units_per_month=data.get('units', 0),
            recommended_kw=data.get('recommended_kw', 0),
            estimated_cost=data.get('final_cost', 0),
            roof_area=data.get('roof_area'),
        )
        return Response({'success': True, 'id': lead.id})

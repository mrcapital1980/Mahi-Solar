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
        import math
        import time
        data = request.data
        monthly_bill = float(data.get('monthly_bill') or 0)
        units = float(data.get('units') or 0)
        system_type = data.get('system_type', 'on_grid')  # 'on_grid', 'hybrid', 'commercial'
        tariff_rate = float(data.get('tariff_rate') or 8.0)

        if units == 0 and monthly_bill > 0:
            units = monthly_bill / tariff_rate
        recommended_kw = max(round(units / 120, 2), 1.0)
        
        # Base cost multiplier depending on system architecture
        if system_type == 'hybrid':
            cost_per_kw = 82000
            system_name = "Hybrid Solar System with Battery Storage"
        elif system_type == 'commercial':
            cost_per_kw = 52000
            system_name = "Commercial B2B 3-Phase Solar Power Plant"
        else:
            cost_per_kw = 60000
            system_name = "Residential On-Grid Solar System"

        estimated_cost = recommended_kw * cost_per_kw
        
        # PM Surya Ghar Subsidy (applicable primarily on Residential On-Grid)
        if system_type == 'on_grid':
            if recommended_kw <= 2:
                subsidy = 18000 * min(recommended_kw, 2)
            else:
                subsidy = 36000 + min((recommended_kw - 2), 1) * 9000
                if recommended_kw >= 3:
                    subsidy = 78000  # Cap at ₹78,000 as per PM Surya Ghar scheme
        else:
            subsidy = 0  # Commercial & off-grid typically utilize tax depreciation / different scheme
        
        final_cost = max(estimated_cost - subsidy, 0)
        roof_area = round(recommended_kw * 90)  # ~90 sqft per kW with high-efficiency 550W panels
        annual_units = round(recommended_kw * 1460)  # ~4 units/day/kW * 365
        annual_savings = round(annual_units * tariff_rate)
        roi_years = round(final_cost / annual_savings, 1) if annual_savings > 0 else 0

        # Environmental & 25-Year Projections
        lifetime_units = round(annual_units * 22.5)  # Degradation factored over 25 yrs
        lifetime_savings = round(lifetime_units * tariff_rate)
        co2_offset_tons = round((lifetime_units * 0.82) / 1000, 1)
        trees_equivalent = round(co2_offset_tons * 45)

        # Dynamic Engineering Bill of Materials (BOM)
        panel_count = math.ceil((recommended_kw * 1000) / 550)
        bom = [
            {
                "category": "Solar PV Modules",
                "item": "550W Mono PERC Bifacial Half-Cut Solar Panels (Tier 1)",
                "specs": "550Wp output, 21.8% cell efficiency, IP68 rated",
                "qty": panel_count,
                "unit": "Panels",
                "warranty": "25 Years Performance Guarantee"
            },
            {
                "category": "Inverter System",
                "item": f"{round(recommended_kw, 1)} kW High-Efficiency MPPT String Inverter",
                "specs": "Pure Sine Wave, Dual MPPT tracking, Integrated Wi-Fi Cloud Monitoring",
                "qty": 1,
                "unit": "Unit",
                "warranty": "10 Years Manufacturer Warranty"
            },
            {
                "category": "Mounting Structure",
                "item": "Elevated Hot-Dip Galvanized / Anodized Aluminum Structure",
                "specs": "Pre-engineered, wind-load resistant up to 150 km/h, corrosion-proof",
                "qty": 1,
                "unit": "Set",
                "warranty": "15 Years Structural Integrity"
            },
            {
                "category": "Electrical & Protection",
                "item": "IP65 Solar DCDB & ACDB Distribution Boxes",
                "specs": "Type-II Surge Protection Devices (SPD), Class-C MCBs & Fuse Protection",
                "qty": 2,
                "unit": "Boxes",
                "warranty": "5 Years Replacement Warranty"
            },
            {
                "category": "Cables & Conduits",
                "item": "4 sq.mm / 6 sq.mm TUV Certified Solar DC Copper Cabling",
                "specs": "Halogen-free, UV & weather resistant, flame retardant conduits",
                "qty": max(round(recommended_kw * 15), 40),
                "unit": "Meters",
                "warranty": "25 Years Operational Life"
            },
            {
                "category": "Safety & Earthing",
                "item": "Dual Chemical Copper-Bonded Earthing + Lightning Protection",
                "specs": "Low-resistance earth electrodes, chemical backfill compound, copper tape",
                "qty": 1,
                "unit": "Complete Kit",
                "warranty": "10 Years Grounding Life"
            },
            {
                "category": "Utility Net-Metering",
                "item": "Bi-Directional Smart Net-Meter Documentation & Discom Liaison",
                "specs": "DGVCL / Torrent Power compliant grid-synchronization inspection",
                "qty": 1,
                "unit": "Liaison Pack",
                "warranty": "100% Approval Guarantee"
            },
            {
                "category": "Engineering & BOS",
                "item": "Turnkey Installation, Testing, Commissioning & Handover",
                "specs": "Certified solar technicians, string megger testing, mobile app integration",
                "qty": 1,
                "unit": "Turnkey Job",
                "warranty": "5 Years Free Comprehensive AMC"
            }
        ]

        if system_type == 'hybrid':
            battery_kwh = max(round(recommended_kw * 2.5), 5)
            bom.insert(2, {
                "category": "Energy Storage",
                "item": f"{battery_kwh} kWh High-Capacity Solar Lithium-ion Battery Bank",
                "specs": "48V / 51.2V LiFePO4, 6000+ life cycles, 90% DoD, smart BMS integration",
                "qty": 1,
                "unit": "Bank",
                "warranty": "10 Years Battery Warranty"
            })

        quotation_ref = f"MS-PROP-{int(time.time()) % 1000000:06d}"

        lead_payload = {
            'name': data.get('name', ''),
            'email': data.get('email', ''),
            'phone': data.get('phone', ''),
            'monthly_bill': monthly_bill,
            'units_per_month': int(units),
            'recommended_kw': recommended_kw,
            'estimated_cost': estimated_cost,
            'roof_area': roof_area,
        }
        if lead_payload['name'] and lead_payload['email']:
            CalculatorLead.objects.create(**lead_payload)

        return Response({
            'success': True,
            'quotation_ref': quotation_ref,
            'system_name': system_name,
            'system_type': system_type,
            'recommended_kw': recommended_kw,
            'estimated_cost': round(estimated_cost),
            'subsidy': round(subsidy),
            'final_cost': round(final_cost),
            'roof_area': roof_area,
            'annual_units': annual_units,
            'annual_savings': annual_savings,
            'monthly_savings': round(annual_savings / 12),
            'roi_years': roi_years,
            'lifetime_units': lifetime_units,
            'lifetime_savings': lifetime_savings,
            'co2_offset_tons': co2_offset_tons,
            'trees_equivalent': trees_equivalent,
            'panel_count': panel_count,
            'bom': bom,
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

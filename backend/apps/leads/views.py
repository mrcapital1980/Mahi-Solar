from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from accounts.decorators import api_login_required
from .models import ContactLead, SiteVisitLead, CalculatorLead
import json


@csrf_exempt
def contact_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except Exception:
            data = request.POST

        name = data.get('name')
        email = data.get('email')
        phone = data.get('phone')
        subject = data.get('subject')
        message_text = data.get('message')

        if not name or not email or not phone or not message_text:
            return JsonResponse({'success': False, 'error': 'Missing required fields'})

        lead = ContactLead.objects.create(
            name=name, email=email, phone=phone,
            subject=subject or 'No Subject', message=message_text
        )

        # Send email notification
        try:
            send_mail(
                subject=f'New Contact: {subject}',
                message=f'Name: {name}\nEmail: {email}\nPhone: {phone}\n\nMessage:\n{message_text}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.CONTACT_EMAIL],
                fail_silently=True,
            )
            # Confirmation to user
            send_mail(
                subject='Thank you for contacting Mahi Solar!',
                message=f'Dear {name},\n\nWe have received your enquiry and will get back to you within 24 hours.\n\nBest regards,\nMahi Solar Team\nSurat, Gujarat\n📞 +91-XXXXXXXXXX',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=True,
            )
        except Exception:
            pass

        return JsonResponse({'success': True, 'id': lead.id, 'message': 'Thank you! We will contact you within 24 hours.'})

    return JsonResponse({'success': False, 'error': 'Only POST method is allowed'})


@csrf_exempt
def site_visit_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except Exception:
            data = request.POST

        name = data.get('name')
        email = data.get('email')
        phone = data.get('phone')
        address = data.get('address')
        city = data.get('city', 'Surat')
        preferred_date = data.get('preferred_date')
        preferred_slot = data.get('preferred_slot') or data.get('preferred_time', '')
        notes = data.get('notes', '')

        if not name or not phone or not address or not preferred_date:
            return JsonResponse({'success': False, 'error': 'Missing required fields'})

        lead = SiteVisitLead.objects.create(
            name=name,
            email=email,
            phone=phone,
            address=address,
            city=city,
            preferred_date=preferred_date,
            preferred_slot=preferred_slot,
            notes=notes,
        )

        try:
            # Notify site owner
            owner_subject = f'New Site Visit Request from {name}'
            owner_message = (
                f"New Site Visit Request Details:\n"
                f"Name: {name}\n"
                f"Phone: {phone}\n"
                f"Email: {email}\n"
                f"Address: {address}, {city}\n"
                f"Preferred Date: {preferred_date}\n"
                f"Preferred Slot: {preferred_slot}\n"
                f"Notes: {notes}"
            )
            send_mail(
                subject=owner_subject,
                message=owner_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.CONTACT_EMAIL],
                fail_silently=True,
            )

            # Notify customer
            customer_subject = 'Site Visit Request Received - Mahi Solar'
            customer_message = (
                f"Dear {name},\n\n"
                f"We have received your site visit request for {preferred_date} during the {preferred_slot}.\n"
                f"Our team will contact you shortly to confirm the appointment.\n\n"
                f"Best regards,\nMahi Solar Team\nSurat, Gujarat\n📞 +91-XXXXXXXXXX"
            )
            if email:
                send_mail(
                    subject=customer_subject,
                    message=customer_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=True,
                )
        except Exception:
            pass

        return JsonResponse({'success': True, 'id': lead.id, 'message': 'Site visit request submitted!'})

    return JsonResponse({'success': False, 'error': 'Only POST method is allowed'})


@api_login_required
def list_contacts(request):
    if not (request.user.is_staff or request.user.is_superuser):
        return JsonResponse({'success': False, 'error': 'Permission denied.'}, status=403)
    leads = ContactLead.objects.all().order_by('-created_at')
    return JsonResponse({
        'success': True,
        'leads': [{
            'id': l.id,
            'name': l.name,
            'email': l.email,
            'phone': l.phone,
            'subject': l.subject,
            'message': l.message,
            'is_resolved': l.is_resolved,
            'created_at': l.created_at.strftime('%d %b %Y %H:%M') if l.created_at else '',
        } for l in leads]
    })


@csrf_exempt
@api_login_required
@require_POST
def toggle_contact_resolve(request, lead_id):
    if not (request.user.is_staff or request.user.is_superuser):
        return JsonResponse({'success': False, 'error': 'Permission denied.'}, status=403)
    lead = get_object_or_404(ContactLead, id=lead_id)
    lead.is_resolved = not lead.is_resolved
    lead.save()
    return JsonResponse({'success': True, 'is_resolved': lead.is_resolved})


@api_login_required
def list_site_visits(request):
    if not (request.user.is_staff or request.user.is_superuser):
        return JsonResponse({'success': False, 'error': 'Permission denied.'}, status=403)
    leads = SiteVisitLead.objects.all().order_by('-created_at')
    return JsonResponse({
        'success': True,
        'leads': [{
            'id': l.id,
            'name': l.name,
            'email': l.email,
            'phone': l.phone,
            'address': l.address,
            'city': l.city,
            'preferred_date': l.preferred_date.strftime('%d %b %Y') if l.preferred_date else '',
            'preferred_slot': l.preferred_slot,
            'notes': l.notes,
            'is_confirmed': l.is_confirmed,
            'created_at': l.created_at.strftime('%d %b %Y %H:%M') if l.created_at else '',
        } for l in leads]
    })


@csrf_exempt
@api_login_required
@require_POST
def toggle_site_visit_confirm(request, lead_id):
    if not (request.user.is_staff or request.user.is_superuser):
        return JsonResponse({'success': False, 'error': 'Permission denied.'}, status=403)
    lead = get_object_or_404(SiteVisitLead, id=lead_id)
    lead.is_confirmed = not lead.is_confirmed
    lead.save()
    return JsonResponse({'success': True, 'is_confirmed': lead.is_confirmed})


@api_login_required
def list_calculator_leads(request):
    if not (request.user.is_staff or request.user.is_superuser):
        return JsonResponse({'success': False, 'error': 'Permission denied.'}, status=403)
    leads = CalculatorLead.objects.all().order_by('-created_at')
    return JsonResponse({
        'success': True,
        'leads': [{
            'id': l.id,
            'name': l.name,
            'email': l.email,
            'phone': l.phone,
            'monthly_bill': float(l.monthly_bill),
            'units_per_month': l.units_per_month,
            'recommended_kw': float(l.recommended_kw),
            'estimated_cost': float(l.estimated_cost),
            'roof_area': float(l.roof_area) if l.roof_area else 0.0,
            'created_at': l.created_at.strftime('%d %b %Y %H:%M') if l.created_at else '',
        } for l in leads]
    })


from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from leads.models import CalculatorLead
import json


def calculator_view(request):
    return JsonResponse({'success': True, 'message': 'Mahi Solar Calculator API is online.'})



@csrf_exempt
@require_POST
def calculate_solar(request):
    try:
        data = json.loads(request.body)
        monthly_bill = float(data.get('monthly_bill', 0))
        units = float(data.get('units', 0))

        # Solar estimation logic
        if units == 0 and monthly_bill > 0:
            units = monthly_bill / 8  # Approx ₹8/unit in Gujarat

        # 1KW generates ~120 units/month in Gujarat (sunny)
        recommended_kw = round(units / 120, 2)
        if recommended_kw < 1:
            recommended_kw = 1.0

        # Cost estimation: ~₹60,000 per KW (installed)
        estimated_cost = recommended_kw * 60000
        # Subsidy ~₹18,000 for first 2KW, ₹9,000 per KW beyond (PM Surya Ghar)
        if recommended_kw <= 2:
            subsidy = 18000 * min(recommended_kw, 2)
        else:
            subsidy = 36000 + (recommended_kw - 2) * 9000
        final_cost = max(estimated_cost - subsidy, 0)

        # Roof area: ~100 sqft per KW
        roof_area = recommended_kw * 100

        # ROI calculation
        annual_savings = units * 12 * 8  # ₹8/unit
        roi_years = round(final_cost / annual_savings, 1) if annual_savings > 0 else 0

        return JsonResponse({
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
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@csrf_exempt
@require_POST
def save_calculator_lead(request):
    try:
        data = json.loads(request.body)
        CalculatorLead.objects.create(
            name=data.get('name'),
            email=data.get('email'),
            phone=data.get('phone'),
            monthly_bill=data.get('monthly_bill', 0),
            units_per_month=data.get('units', 0),
            recommended_kw=data.get('recommended_kw', 0),
            estimated_cost=data.get('final_cost', 0),
            roof_area=data.get('roof_area'),
        )
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

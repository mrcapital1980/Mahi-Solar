from functools import wraps
from django.http import JsonResponse

def api_login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            auth_header = request.headers.get('Authorization') or request.META.get('HTTP_AUTHORIZATION')
            if auth_header:
                parts = auth_header.split()
                if len(parts) == 2 and parts[0].lower() in ['token', 'bearer']:
                    token_key = parts[1]
                    try:
                        from rest_framework.authtoken.models import Token
                        token = Token.objects.filter(key=token_key).select_related('user').first()
                        if token and token.user and token.user.is_active:
                            request.user = token.user
                    except Exception:
                        pass
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'error': 'Authentication credentials were not provided.'}, status=401)
        return view_func(request, *args, **kwargs)
    return _wrapped_view


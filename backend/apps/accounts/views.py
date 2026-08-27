from django.contrib.auth import login, logout, authenticate
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import UserProfile
from .decorators import api_login_required
import json


@csrf_exempt
def register_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except Exception:
            data = request.POST

        from django.contrib.auth.models import User
        from rest_framework.authtoken.models import Token
        username = data.get('username')
        password = data.get('password')
        email = data.get('email', '')
        first_name = data.get('first_name', '')
        last_name = data.get('last_name', '')

        if not username or not password:
            return JsonResponse({'success': False, 'error': 'Username and password are required'}, status=400)

        if User.objects.filter(username=username).exists():
            return JsonResponse({'success': False, 'error': 'Username already exists'}, status=400)

        user = User.objects.create_user(
            username=username, password=password, email=email,
            first_name=first_name, last_name=last_name
        )
        UserProfile.objects.get_or_create(user=user)
        login(request, user)
        token, _ = Token.objects.get_or_create(user=user)
        return JsonResponse({
            'success': True,
            'id': user.id,
            'access': token.key,
            'token': token.key,
            'username': user.username,
            'first_name': user.first_name,
            'email': user.email,
            'is_superuser': user.is_superuser,
            'is_staff': user.is_staff,
        }, status=201)
    return JsonResponse({'success': False, 'error': 'Only POST method is allowed'}, status=405)


@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except Exception:
            data = request.POST

        username = data.get('username')
        password = data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            from rest_framework.authtoken.models import Token
            token, _ = Token.objects.get_or_create(user=user)
            return JsonResponse({
                'success': True,
                'access': token.key,
                'token': token.key,
                'first_name': user.first_name or user.username,
                'email': user.email,
                'username': user.username,
                'is_superuser': user.is_superuser,
                'is_staff': user.is_staff,
            })
        return JsonResponse({'success': False, 'error': 'Invalid credentials'}, status=400)
    return JsonResponse({'success': False, 'error': 'Only POST method is allowed'}, status=405)



def logout_view(request):
    logout(request)
    return JsonResponse({'success': True, 'message': 'Logged out'})


@api_login_required
@csrf_exempt
def profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'GET':
        return JsonResponse({
            'success': True,
            'profile': {
                'username': request.user.username,
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'email': request.user.email,
                'phone': profile.phone if hasattr(profile, 'phone') else '',
                'address': profile.address if hasattr(profile, 'address') else '',
                'city': profile.city if hasattr(profile, 'city') else '',
                'is_superuser': request.user.is_superuser,
                'is_staff': request.user.is_staff,
            }
        })

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except Exception:
            data = request.POST
        # Update user fields
        request.user.first_name = data.get('first_name', request.user.first_name)
        request.user.last_name = data.get('last_name', request.user.last_name)
        request.user.email = data.get('email', request.user.email)
        request.user.save()
        # Update profile fields
        if hasattr(profile, 'phone'):
            profile.phone = data.get('phone', profile.phone)
        if hasattr(profile, 'address'):
            profile.address = data.get('address', profile.address)
        if hasattr(profile, 'city'):
            profile.city = data.get('city', profile.city)
        profile.save()
        return JsonResponse({'success': True, 'message': 'Profile updated'})

    return JsonResponse({'success': False, 'error': 'Method not allowed'})


@api_login_required
def users_list_view(request):
    if not (request.user.is_staff or request.user.is_superuser):
        return JsonResponse({'success': False, 'error': 'Permission denied. Admin privileges required.'}, status=403)

    from django.contrib.auth.models import User
    users = User.objects.all().order_by('-date_joined')
    user_data = []
    for u in users:
        phone = ''
        if hasattr(u, 'profile') and u.profile:
            phone = u.profile.phone or ''
        user_data.append({
            'id': u.id,
            'username': u.username,
            'email': u.email,
            'first_name': u.first_name,
            'last_name': u.last_name,
            'phone': phone,
            'is_staff': u.is_staff,
            'is_superuser': u.is_superuser,
            'date_joined': u.date_joined.strftime('%d %b %Y, %H:%M') if u.date_joined else '',
        })
    return JsonResponse({'success': True, 'users': user_data})


@csrf_exempt
@api_login_required
def toggle_admin_view(request):
    if not (request.user.is_staff or request.user.is_superuser):
        return JsonResponse({'success': False, 'error': 'Permission denied. Only Superusers can assign admin rights.'}, status=403)

    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Only POST method allowed'}, status=405)

    try:
        data = json.loads(request.body)
    except Exception:
        data = request.POST

    from django.contrib.auth.models import User
    user_identifier = data.get('user_id') or data.get('username') or data.get('email')
    action = data.get('action', 'promote') # 'promote' or 'demote'

    if not user_identifier:
        return JsonResponse({'success': False, 'error': 'User ID, Username, or Email required.'}, status=400)

    user = None
    if str(user_identifier).isdigit():
        user = User.objects.filter(id=int(user_identifier)).first()
    if not user:
        user = User.objects.filter(username=user_identifier).first()
    if not user:
        user = User.objects.filter(email=user_identifier).first()

    if not user:
        return JsonResponse({'success': False, 'error': f'User "{user_identifier}" not found.'}, status=404)

    if action == 'promote':
        user.is_staff = True
        user.is_superuser = True
        user.save()
        return JsonResponse({'success': True, 'message': f'User "{user.username}" ({user.email}) has been granted FULL ADMIN PARTNER privileges!'})
    elif action == 'demote':
        if user == request.user:
            return JsonResponse({'success': False, 'error': 'You cannot demote your own active admin account!'}, status=400)
        user.is_staff = False
        user.is_superuser = False
        user.save()
        return JsonResponse({'success': True, 'message': f'Admin privileges revoked for user "{user.username}".'})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid action. Use "promote" or "demote".'}, status=400)


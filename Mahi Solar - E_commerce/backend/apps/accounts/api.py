from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from .models import UserProfile
from .forms import ProfileUpdateForm


class AuthViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    def _is_authenticated(self, request):
        return request.user and request.user.is_authenticated

    def list(self, request):
        if self._is_authenticated(request):
            profile, _ = UserProfile.objects.get_or_create(user=request.user)
            return Response({
                'success': True,
                'user': {
                    'id': request.user.id,
                    'username': request.user.username,
                    'first_name': request.user.first_name,
                    'last_name': request.user.last_name,
                    'email': request.user.email,
                    'phone': getattr(profile, 'phone', ''),
                    'address': getattr(profile, 'address', ''),
                    'city': getattr(profile, 'city', ''),
                },
            })
        return Response({'success': False, 'error': 'Not authenticated'}, status=401)

    @action(detail=False, methods=['post'])
    def register(self, request):
        data = request.data
        username = data.get('username')
        password = data.get('password')
        email = data.get('email', '')
        first_name = data.get('first_name', '')
        last_name = data.get('last_name', '')
        if User.objects.filter(username=username).exists():
            return Response({'success': False, 'error': 'Username already exists'}, status=400)
        user = User.objects.create_user(
            username=username, password=password, email=email,
            first_name=first_name, last_name=last_name
        )
        UserProfile.objects.get_or_create(user=user)
        login(request, user)
        from rest_framework.authtoken.models import Token
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'success': True,
            'id': user.id,
            'access': token.key,
            'token': token.key,
            'username': user.username,
            'first_name': user.first_name,
            'email': user.email,
            'is_superuser': user.is_superuser,
            'is_staff': user.is_staff,
        })

    @action(detail=False, methods=['post'])
    def login(self, request):
        data = request.data
        username = data.get('username')
        password = data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            from rest_framework.authtoken.models import Token
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'success': True,
                'access': token.key,
                'token': token.key,
                'first_name': user.first_name or user.username,
                'email': user.email,
                'username': user.username,
                'is_superuser': user.is_superuser,
                'is_staff': user.is_staff,
            })
        return Response({'success': False, 'error': 'Invalid credentials'}, status=400)

    @action(detail=False, methods=['post'])
    def logout(self, request):
        logout(request)
        return Response({'success': True, 'message': 'Logged out'})

    @action(detail=False, methods=['post'])
    def profile(self, request):
        if not self._is_authenticated(request):
            return Response({'success': False, 'error': 'Not authenticated'}, status=401)
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        data = request.data
        request.user.first_name = data.get('first_name', request.user.first_name)
        request.user.last_name = data.get('last_name', request.user.last_name)
        request.user.email = data.get('email', request.user.email)
        request.user.save()
        for field in ['phone', 'address', 'city']:
            setattr(profile, field, data.get(field, getattr(profile, field, '')))
        profile.save()
        return Response({'success': True, 'message': 'Profile updated'})

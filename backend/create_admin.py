import os
import django

if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
django.setup()

from django.contrib.auth.models import User
from accounts.models import UserProfile

admins = [
    {
        'username': 'admin',
        'email': 'mrcapital1980@gmail.com',
        'first_name': 'Manish',
        'last_name': 'Moradiya',
        'phone': '+91 93773 09325',
        'password': os.getenv('ADMIN_PASSWORD', 'MahiSolarAdmin@2026')
    },
    {
        'username': 'manish_moradiya',
        'email': 'mrcapital1980@gmail.com',
        'first_name': 'Manish',
        'last_name': 'Moradiya',
        'phone': '+91 93773 09325',
        'password': os.getenv('ADMIN_PASSWORD', 'MahiSolarAdmin@2026')
    }
]

for data in admins:
    try:
        user, created = User.objects.get_or_create(
            username=data['username'],
            defaults={
                'email': data['email'],
                'first_name': data['first_name'],
                'last_name': data['last_name'],
                'is_staff': True,
                'is_superuser': True
            }
        )
        user.set_password(data['password'])
        user.email = data['email']
        user.first_name = data['first_name']
        user.last_name = data['last_name']
        user.is_staff = True
        user.is_superuser = True
        user.save()

        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.phone = data['phone']
        profile.city = 'Surat'
        profile.state = 'Gujarat'
        profile.save()

        status = "Created" if created else "Updated"
        print(f"{status} superuser: {user.username} ({user.email})")
    except Exception as e:
        print(f"Admin provisioning note for {data['username']}: {e}")

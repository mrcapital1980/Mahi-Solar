import os
import django

if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
django.setup()

from django.contrib.auth.models import User

username = os.getenv('ADMIN_USERNAME', 'admin')
email = os.getenv('ADMIN_EMAIL', 'contact@mahisolar.co.in')
password = os.getenv('ADMIN_PASSWORD', 'MahiSolarAdmin@2026')

try:
    user, created = User.objects.get_or_create(username=username, defaults={'email': email, 'is_staff': True, 'is_superuser': True})
    user.set_password(password)
    user.is_staff = True
    user.is_superuser = True
    user.save()

    if created:
        print(f"Created new superuser: {username}")
    else:
        print(f"Updated password for superuser: {username}")
except Exception as e:
    print(f"Admin provisioning note: {e}")

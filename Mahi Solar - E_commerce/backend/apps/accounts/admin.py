from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'city', 'state', 'created_at']
    search_fields = ['user__username', 'user__email', 'phone']
    list_filter = ['city', 'state']

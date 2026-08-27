from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('users-list/', views.users_list_view, name='users_list'),
    path('toggle-admin/', views.toggle_admin_view, name='toggle_admin'),
]

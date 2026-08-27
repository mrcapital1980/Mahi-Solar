from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.views.static import serve
from products.views import index
from rest_framework.routers import DefaultRouter
from products.api import ProductViewSet, CategoryViewSet
from orders.api import CartViewSet, OrderViewSet
from leads.api import ContactLeadViewSet, SiteVisitLeadViewSet, CalculatorAPIViewSet
from accounts.api import AuthViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='api-product')
router.register(r'categories', CategoryViewSet, basename='api-category')
router.register(r'cart', CartViewSet, basename='api-cart')
router.register(r'orders', OrderViewSet, basename='api-order')
router.register(r'contact', ContactLeadViewSet, basename='api-contact')
router.register(r'site-visit', SiteVisitLeadViewSet, basename='api-site-visit')
router.register(r'calculator', CalculatorAPIViewSet, basename='api-calculator')
router.register(r'auth', AuthViewSet, basename='api-auth')

urlpatterns = [
    path('secure-portal/', admin.site.urls),
    path('', index, name='index'),
    path('accounts/', include('accounts.urls')),
    path('products/', include('products.urls')),
    path('orders/', include('orders.urls')),
    path('leads/', include('leads.urls')),
    path('blog/', include('blog.urls')),
    path('calculator/', include('calculator.urls')),
    path('api/', include(router.urls)),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

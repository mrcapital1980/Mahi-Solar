from django.urls import path
from . import views

urlpatterns = [
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('payment/razorpay/<uuid:order_id>/', views.razorpay_payment, name='razorpay_payment'),
    path('payment/qr/<uuid:order_id>/', views.qr_payment, name='qr_payment'),
    path('success/<uuid:order_id>/', views.order_success, name='order_success'),
    path('my-orders/', views.order_list, name='order_list'),
    path('my-orders/<uuid:order_id>/', views.order_detail, name='order_detail'),
    path('cancel-order/<int:order_id>/', views.cancel_order, name='cancel_order'),
    path('return-order/<int:order_id>/', views.return_order, name='return_order'),
    path('update-status/<int:order_id>/', views.update_order_status, name='update_order_status'),

]

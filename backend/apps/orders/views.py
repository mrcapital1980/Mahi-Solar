from django.shortcuts import get_object_or_404
from accounts.decorators import api_login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import Cart, CartItem, Order, OrderItem
from products.models import Product
import json
from django.core.mail import send_mail


def send_order_notification(order):
    try:
        # Notify the site owner
        owner_subject = f'New Order Received: {str(order.order_id)[:8].upper()}'
        owner_message = (
            f"New Order Details:\n"
            f"Order ID: {order.order_id}\n"
            f"Customer: {order.full_name}\n"
            f"Phone: {order.phone}\n"
            f"Email: {order.email}\n"
            f"Total Amount: ₹{order.total_amount}\n"
            f"Payment Method: {order.payment_method}\n"
        )
        send_mail(
            subject=owner_subject,
            message=owner_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.CONTACT_EMAIL],
            fail_silently=True,
        )

        # Notify the customer
        customer_subject = f'Order Confirmation - Mahi Solar ({str(order.order_id)[:8].upper()})'
        customer_message = (
            f"Hi {order.full_name},\n\n"
            f"Thank you for your order!\n"
            f"Your order ID is: {order.order_id}\n"
            f"Total Amount: ₹{order.total_amount}\n\n"
            f"We will process your order soon.\n\n"
            f"Best regards,\nMahi Solar Team"
        )
        if order.email:
            send_mail(
                subject=customer_subject,
                message=customer_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[order.email],
                fail_silently=True,
            )
    except Exception:
        pass


def get_or_create_cart(user):
    cart, _ = Cart.objects.get_or_create(user=user, is_checked_out=False)
    return cart


@api_login_required
def cart_view(request):
    cart = get_or_create_cart(request.user)
    items = [{
        'id': item.id,
        'product_id': item.product.id,
        'name': item.product.name,
        'slug': item.product.slug,
        'price': float(item.product.price) if item.product.price else 0,
        'discounted_price': float(item.product.discounted_price) if item.product.discounted_price else None,
        'effective_price': float(item.product.effective_price),
        'quantity': item.quantity,
        'total': float(item.total),
        'image': item.product.image.url if item.product.image else None,
    } for item in cart.items.all()]
    return JsonResponse({
        'success': True,
        'cart': {
            'items': items,
            'item_count': cart.item_count,
            'total': float(cart.total),
        }
    })


@csrf_exempt
@api_login_required
@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    cart = get_or_create_cart(request.user)
    item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        item.quantity += 1
        item.save()
    return JsonResponse({'success': True, 'cart_count': cart.item_count})


@csrf_exempt
@api_login_required
@require_POST
def update_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    try:
        data = json.loads(request.body)
        quantity = int(data.get('quantity', 1))
    except Exception:
        quantity = int(request.POST.get('quantity', 1))

    if quantity < 1:
        item.delete()
        msg = 'Item removed from cart.'
    else:
        item.quantity = quantity
        item.save()
        msg = 'Cart updated.'

    cart = get_or_create_cart(request.user)
    return JsonResponse({'success': True, 'message': msg, 'cart_count': cart.item_count})


@csrf_exempt
@api_login_required
@require_POST
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    item.delete()
    cart = get_or_create_cart(request.user)
    return JsonResponse({'success': True, 'message': 'Item removed', 'cart_count': cart.item_count})


@csrf_exempt
@api_login_required
def checkout_view(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Only POST method is allowed'}, status=405)

    cart = get_or_create_cart(request.user)

    try:
        data = json.loads(request.body)
    except Exception:
        data = request.POST

    # Sync cart items from payload if DB cart is empty
    if not cart.items.exists() and data.get('items'):
        for item_data in data.get('items'):
            prod_id = item_data.get('id') or item_data.get('product_id')
            if prod_id:
                product = Product.objects.filter(id=prod_id, is_active=True).first()
                if product:
                    c_item, _ = CartItem.objects.get_or_create(cart=cart, product=product)
                    c_item.quantity = int(item_data.get('quantity', 1))
                    c_item.save()

    if not cart.items.exists():
        return JsonResponse({'success': False, 'error': 'Cart is empty'}, status=400)

    payment_method = data.get('payment_method', 'cod')
    order = Order.objects.create(
        user=request.user,
        cart=cart,
        full_name=data.get('full_name', ''),
        email=data.get('email', ''),
        phone=data.get('phone', ''),
        address=data.get('address', ''),
        city=data.get('city', ''),
        state=data.get('state', 'Gujarat'),
        pincode=data.get('pincode', ''),
        payment_method=payment_method,
        total_amount=cart.total,
        notes=data.get('notes', ''),
    )
    for item in cart.items.all():
        OrderItem.objects.create(
            order=order,
            product=item.product,
            product_name=item.product.name,
            price=item.product.effective_price,
            quantity=item.quantity,
        )

    cart.is_checked_out = True
    cart.save()

    if payment_method == 'cod':
        order.status = 'confirmed'
        order.save()
        send_order_notification(order)

    return JsonResponse({
        'success': True,
        'order_id': str(order.order_id),
        'payment_method': payment_method,
        'total_amount': float(order.total_amount),
        'message': f'Order #{str(order.order_id)[:8].upper()} placed successfully!',
    })


@csrf_exempt
@api_login_required
def razorpay_payment(request, order_id):
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except Exception:
            data = request.POST
        order.razorpay_payment_id = data.get('razorpay_payment_id', '')
        order.payment_status = True
        order.status = 'confirmed'
        order.save()
        send_order_notification(order)
        return JsonResponse({'success': True, 'message': 'Payment successful! Order confirmed.'})
    return JsonResponse({'success': True, 'order_id': str(order.order_id), 'razorpay_key': settings.RAZORPAY_KEY_ID})


@csrf_exempt
@api_login_required
def qr_payment(request, order_id):
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    if request.method == 'POST':
        order.payment_status = True
        order.status = 'confirmed'
        order.save()
        send_order_notification(order)
        return JsonResponse({'success': True, 'message': 'Payment confirmed! Order placed successfully.'})
    return JsonResponse({'success': True, 'order_id': str(order.order_id)})


@api_login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    return JsonResponse({
        'success': True,
        'order': {
            'order_id': str(order.order_id),
            'status': order.status,
            'total_amount': float(order.total_amount),
            'payment_method': order.payment_method,
            'created_at': order.created_at.strftime('%d %b %Y') if order.created_at else '',
        }
    })


@api_login_required
def order_list(request):
    if request.user.is_staff or request.user.is_superuser:
        orders = Order.objects.all()
    else:
        orders = Order.objects.filter(user=request.user)
    return JsonResponse({
        'success': True,
        'orders': [{
            'id': o.id,
            'order_id': str(o.order_id),
            'status': o.status,
            'total_amount': float(o.total_amount),
            'payment_method': o.payment_method,
            'full_name': o.full_name,
            'created_at': o.created_at.strftime('%d %b %Y') if o.created_at else '',
            'item_count': o.items.count(),
        } for o in orders],
    })


@api_login_required
def order_detail(request, order_id):
    if request.user.is_staff or request.user.is_superuser:
        order = get_object_or_404(Order, order_id=order_id)
    else:
        order = get_object_or_404(Order, order_id=order_id, user=request.user)
    return JsonResponse({
        'success': True,
        'order': {
            'id': order.id,
            'order_id': str(order.order_id),
            'status': order.status,
            'total_amount': float(order.total_amount),
            'payment_method': order.payment_method,
            'full_name': order.full_name,
            'email': order.email,
            'phone': order.phone,
            'address': order.address,
            'city': order.city,
            'state': order.state,
            'pincode': order.pincode,
            'notes': order.notes,
            'created_at': order.created_at.strftime('%d %b %Y') if order.created_at else '',
            'items': [{
                'product_name': item.product_name,
                'price': float(item.price),
                'quantity': item.quantity,
                'total': float(item.subtotal),
            } for item in order.items.all()],
        }
    })


@csrf_exempt
@api_login_required
@require_POST
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    # Allow customer cancellation before the order starts being processed/shipped.
    if order.status in ['pending', 'confirmed']:
        order.status = 'cancelled'
        order.save()
        return JsonResponse({'success': True, 'message': 'Order cancelled successfully.'})
    else:
        return JsonResponse({'success': False, 'error': 'Cannot cancel this order.'})


@csrf_exempt
@api_login_required
@require_POST
def return_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.status == 'placed':
        order.status = 'returned'
        order.save()
        return JsonResponse({'success': True, 'message': 'Order return requested.'})
    else:
        return JsonResponse({'success': False, 'error': 'Return not allowed.'})


@csrf_exempt
@api_login_required
@require_POST
def update_order_status(request, order_id):
    if not (request.user.is_staff or request.user.is_superuser):
        return JsonResponse({'success': False, 'error': 'Permission denied.'}, status=403)
    
    order = get_object_or_404(Order, id=order_id)
    try:
        data = json.loads(request.body)
        status_val = data.get('status')
    except Exception:
        status_val = request.POST.get('status')
        
    if not status_val:
        return JsonResponse({'success': False, 'error': 'Status field is required.'}, status=400)
        
    valid_statuses = [choice[0] for choice in Order.STATUS_CHOICES]
    if status_val not in valid_statuses:
        return JsonResponse({'success': False, 'error': 'Invalid status.'}, status=400)
        
    order.status = status_val
    order.save()
    return JsonResponse({'success': True, 'message': f'Order status updated to {status_val}'})
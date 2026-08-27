from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from .models import Cart, CartItem, Order, OrderItem
from leads.models import ContactLead, SiteVisitLead, CalculatorLead
from orders.serializers import CartSerializer, CartItemSerializer, OrderSerializer
from leads.serializers import ContactLeadSerializer, SiteVisitLeadSerializer, CalculatorLeadSerializer


class CartViewSet(viewsets.ViewSet):
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def list(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user, is_checked_out=False)
        serializer = CartSerializer(cart, context={'request': request})
        return Response({'success': True, 'cart': serializer.data})

    @action(detail=False, methods=['post'])
    def add_item(self, request):
        product_id = request.data.get('product_id')
        if not product_id:
            return Response({'success': False, 'error': 'product_id required'}, status=400)

        from products.models import Product
        product = get_object_or_404(Product, id=product_id, is_active=True)
        cart, _ = Cart.objects.get_or_create(user=request.user, is_checked_out=False)
        item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            item.quantity += 1
            item.save()

        serializer = CartSerializer(cart, context={'request': request})
        return Response({'success': True, 'cart_count': cart.item_count, 'cart': serializer.data})

    @action(detail=False, methods=['post'])
    def update_item(self, request):
        item_id = request.data.get('item_id')
        quantity = int(request.data.get('quantity', 1))
        item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)

        if quantity < 1:
            item.delete()
            msg = 'Item removed.'
        else:
            item.quantity = quantity
            item.save()
            msg = 'Cart updated.'

        cart, _ = Cart.objects.get_or_create(user=request.user, is_checked_out=False)
        serializer = CartSerializer(cart, context={'request': request})
        return Response({'success': True, 'message': msg, 'cart': serializer.data})

    @action(detail=False, methods=['post'])
    def remove_item(self, request):
        item_id = request.data.get('item_id')
        item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        item.delete()
        cart, _ = Cart.objects.get_or_create(user=request.user, is_checked_out=False)
        serializer = CartSerializer(cart, context={'request': request})
        return Response({'success': True, 'message': 'Item removed', 'cart': serializer.data})


class OrderViewSet(viewsets.ViewSet):
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [AllowAny]

    def list(self, request):
        if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
            orders = Order.objects.all().order_by('-created_at')
        elif request.user.is_authenticated:
            orders = Order.objects.filter(user=request.user).order_by('-created_at')
        else:
            orders = Order.objects.none()
        serializer = OrderSerializer(orders, many=True)
        return Response({'success': True, 'orders': serializer.data})

    def retrieve(self, request, pk=None):
        if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
            order = get_object_or_404(Order, order_id=pk)
        elif request.user.is_authenticated:
            order = get_object_or_404(Order, order_id=pk, user=request.user)
        else:
            return Response({'success': False, 'error': 'Authentication required'}, status=401)
        serializer = OrderSerializer(order)
        return Response({'success': True, 'order': serializer.data})

    def create(self, request):
        data = request.data
        items_payload = data.get('items', [])
        
        user = request.user if request.user.is_authenticated else None
        cart = None
        if user:
            cart = Cart.objects.filter(user=user, is_checked_out=False).first()
        
        # Create order even if no DB cart exists (guest or local storage checkout)
        total_amount = float(data.get('total_amount', 0))
        
        order = Order.objects.create(
            user=user,
            cart=cart,
            full_name=data.get('full_name', ''),
            email=data.get('email', ''),
            phone=data.get('phone', ''),
            address=data.get('address', ''),
            city=data.get('city', ''),
            state=data.get('state', 'Gujarat'),
            pincode=data.get('pincode', ''),
            payment_method=data.get('payment_method', 'cod'),
            total_amount=total_amount,
            notes=data.get('notes', ''),
        )
        
        # Populate OrderItems from DB cart or from payload items
        if cart and cart.items.exists():
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
        elif items_payload:
            from products.models import Product
            calc_total = 0
            for item_data in items_payload:
                prod_id = item_data.get('id') or item_data.get('product_id')
                product = Product.objects.filter(id=prod_id).first() if prod_id else None
                p_name = item_data.get('name') or (product.name if product else 'Solar Product')
                p_price = float(item_data.get('discounted_price') or item_data.get('price') or (product.effective_price if product else 0))
                p_qty = int(item_data.get('quantity', 1))
                calc_total += p_price * p_qty
                
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_name=p_name,
                    price=p_price,
                    quantity=p_qty,
                )
            if total_amount == 0:
                order.total_amount = calc_total
                order.save()

        payment_method = data.get('payment_method', 'cod')
        if payment_method == 'cod':
            order.status = 'confirmed'
            order.save()
            _send_order_notification(order)

        serializer = OrderSerializer(order)
        return Response({
            'success': True,
            'order_id': str(order.order_id),
            'order': serializer.data,
        })

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        order = get_object_or_404(Order, order_id=pk, user=request.user)
        if order.status in ['pending', 'confirmed']:
            order.status = 'cancelled'
            order.save()
            return Response({'success': True, 'message': 'Order cancelled.'})
        return Response({'success': False, 'error': 'Cannot cancel this order.'}, status=400)

    @action(detail=True, methods=['post'])
    def return_order(self, request, pk=None):
        order = get_object_or_404(Order, order_id=pk, user=request.user)
        if order.status == 'placed':
            order.status = 'returned'
            order.save()
            return Response({'success': True, 'message': 'Return requested.'})
        return Response({'success': False, 'error': 'Return not allowed.'}, status=400)


class ContactLeadViewSet(viewsets.ModelViewSet):
    queryset = ContactLead.objects.all()
    serializer_class = ContactLeadSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        lead = self.perform_create(serializer)
        _send_contact_email(lead)
        return Response({'success': True, 'id': lead.id, 'message': 'Thank you! We will contact you within 24 hours.'}, status=201)

    def perform_create(self, serializer):
        return serializer.save()


class SiteVisitLeadViewSet(viewsets.ModelViewSet):
    queryset = SiteVisitLead.objects.all()
    serializer_class = SiteVisitLeadSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        lead = self.perform_create(serializer)
        _send_site_visit_email(lead)
        return Response({'success': True, 'id': lead.id, 'message': 'Site visit request submitted!'}, status=201)

    def perform_create(self, serializer):
        return serializer.save()


class CalculatorAPIViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    @action(detail=False, methods=['post'])
    def calculate(self, request):
        data = request.data
        monthly_bill = float(data.get('monthly_bill', 0))
        units = float(data.get('units', 0))
        if units == 0 and monthly_bill > 0:
            units = monthly_bill / 8
        recommended_kw = round(units / 120, 2)
        if recommended_kw < 1:
            recommended_kw = 1.0
        estimated_cost = recommended_kw * 60000
        if recommended_kw <= 2:
            subsidy = 18000 * min(recommended_kw, 2)
        else:
            subsidy = 36000 + (recommended_kw - 2) * 9000
        final_cost = max(estimated_cost - subsidy, 0)
        roof_area = recommended_kw * 100
        annual_savings = units * 12 * 8
        roi_years = round(final_cost / annual_savings, 1) if annual_savings > 0 else 0

        if data.get('name') and data.get('email'):
            CalculatorLead.objects.create(
                name=data.get('name'),
                email=data.get('email'),
                phone=data.get('phone', ''),
                monthly_bill=monthly_bill,
                units_per_month=units,
                recommended_kw=recommended_kw,
                estimated_cost=estimated_cost,
                roof_area=roof_area,
            )

        return Response({
            'success': True,
            'recommended_kw': recommended_kw,
            'estimated_cost': round(estimated_cost),
            'subsidy': round(subsidy),
            'final_cost': round(final_cost),
            'roof_area': round(roof_area),
            'annual_savings': round(annual_savings),
            'roi_years': roi_years,
            'monthly_savings': round(annual_savings / 12),
        })

    @action(detail=False, methods=['post'])
    def save_lead(self, request):
        data = request.data
        lead = CalculatorLead.objects.create(
            name=data.get('name', ''),
            email=data.get('email', ''),
            phone=data.get('phone', ''),
            monthly_bill=data.get('monthly_bill', 0),
            units_per_month=data.get('units', 0),
            recommended_kw=data.get('recommended_kw', 0),
            estimated_cost=data.get('final_cost', 0),
            roof_area=data.get('roof_area'),
        )
        return Response({'success': True, 'id': lead.id})


def _send_contact_email(lead):
    try:
        send_mail(
            subject=f'New Contact: {lead.subject}',
            message=f'Name: {lead.name}\nEmail: {lead.email}\nPhone: {lead.phone}\n\nMessage:\n{lead.message}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.CONTACT_EMAIL], fail_silently=True,
        )
        send_mail(
            subject='Thank you for contacting Mahi Solar!',
            message=f'Dear {lead.name},\n\nWe have received your enquiry and will get back to you within 24 hours.\n\nBest regards,\nMahi Solar Team',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[lead.email], fail_silently=True,
        )
    except Exception:
        pass


def _send_site_visit_email(lead):
    try:
        owner_msg = (
            f"New Site Visit Request Details:\n"
            f"Name: {lead.name}\nPhone: {lead.phone}\nEmail: {lead.email}\n"
            f"Address: {lead.address}, {lead.city}\n"
            f"Preferred Date: {lead.preferred_date}\nSlot: {lead.preferred_slot}\nNotes: {lead.notes}"
        )
        send_mail(
            subject=f'New Site Visit Request from {lead.name}',
            message=owner_msg,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.CONTACT_EMAIL], fail_silently=True,
        )
        customer_msg = (
            f"Dear {lead.name},\n\nWe have received your site visit request for {lead.preferred_date} "
            f"during the {lead.preferred_slot}. Our team will contact you shortly.\n\nBest regards,\nMahi Solar Team"
        )
        send_mail(
            subject='Site Visit Request Received - Mahi Solar',
            message=customer_msg,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[lead.email], fail_silently=True,
        )
    except Exception:
        pass


def _send_order_notification(order):
    try:
        send_mail(
            subject=f'New Order Received: {str(order.order_id)[:8].upper()}',
            message=f"New Order Details:\nOrder ID: {order.order_id}\nCustomer: {order.full_name}\nPhone: {order.phone}\nEmail: {order.email}\nTotal Amount: ₹{order.total_amount}\nPayment Method: {order.payment_method}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.CONTACT_EMAIL], fail_silently=True,
        )
        send_mail(
            subject=f'Order Confirmation - Mahi Solar ({str(order.order_id)[:8].upper()})',
            message=f"Hi {order.full_name},\n\nThank you for your order!\nYour order ID is: {order.order_id}\nTotal Amount: ₹{order.total_amount}\n\nBest regards,\nMahi Solar Team",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.email], fail_silently=True,
        )
    except Exception:
        pass

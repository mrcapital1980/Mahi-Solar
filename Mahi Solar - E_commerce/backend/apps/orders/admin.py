from django.contrib import admin
from .models import Cart, CartItem, Order, OrderItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ['product', 'quantity', 'added_at']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'is_checked_out', 'item_count', 'total', 'created_at']
    list_filter = ['is_checked_out', 'created_at']
    search_fields = ['user__username', 'user__email']
    inlines = [CartItemInline]

    def item_count(self, obj):
        return obj.item_count
    item_count.short_description = 'Items'

    def total(self, obj):
        return f"₹{obj.total:,.2f}"
    total.short_description = 'Total'


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'product_name', 'price', 'quantity']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_id_short', 'user', 'full_name', 'payment_method', 'payment_status', 'status', 'total_amount', 'created_at']
    list_filter = ['status', 'payment_method', 'payment_status', 'created_at']
    search_fields = ['user__username', 'full_name', 'email', 'phone']
    list_editable = ['status']
    inlines = [OrderItemInline]
    readonly_fields = ['order_id', 'user', 'cart', 'created_at']

    def order_id_short(self, obj):
        return str(obj.order_id)[:8].upper()
    order_id_short.short_description = 'Order ID'

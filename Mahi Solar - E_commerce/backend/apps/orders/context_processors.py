from .models import Cart


def cart_count(request):
    count = 0
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user, is_checked_out=False).first()
        if cart:
            count = cart.item_count
    return {'cart_count': count}

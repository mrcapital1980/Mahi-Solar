from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.http import JsonResponse
from .models import Product, Category, Review


def index(request):
    featured_products = Product.objects.filter(is_active=True, is_featured=True)[:6]
    categories = Category.objects.filter(is_active=True)
    recent_products = Product.objects.filter(is_active=True)[:8]
    
    return JsonResponse({
        'success': True,
        'featured_products': [{
            'id': p.id,
            'name': p.name,
            'slug': p.slug,
            'image': p.image.url if p.image else None,
            'price': float(p.price) if p.price is not None else None,
            'discounted_price': float(p.discounted_price) if p.discounted_price is not None else None,
            'discount_percent': p.discount_percent,
            'avg_rating': p.avg_rating,
            'reviews_count': p.reviews.count(),
            'category': {'id': p.category.id, 'name': p.category.name, 'slug': p.category.slug} if p.category else None,
        } for p in featured_products],
        'categories': [{
            'id': c.id,
            'name': c.name,
            'slug': c.slug,
            'image': c.image.url if c.image else None
        } for c in categories],
        'recent_products': [{
            'id': p.id,
            'name': p.name,
            'slug': p.slug,
            'image': p.image.url if p.image else None,
            'price': float(p.price) if p.price is not None else None,
            'discounted_price': float(p.discounted_price) if p.discounted_price is not None else None,
            'discount_percent': p.discount_percent,
            'avg_rating': p.avg_rating,
            'reviews_count': p.reviews.count(),
            'category': {'id': p.category.id, 'name': p.category.name, 'slug': p.category.slug} if p.category else None,
        } for p in recent_products],
    })


def product_list(request):
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.filter(is_active=True)
    category_slug = request.GET.get('category')
    search_query = request.GET.get('q', '')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    selected_category = None

    if category_slug:
        selected_category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=selected_category)

    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(brand__icontains=search_query)
        )

    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    return JsonResponse({
        'success': True,
        'products': [{
            'id': p.id,
            'name': p.name,
            'slug': p.slug,
            'image': p.image.url if p.image else None,
            'price': float(p.price) if p.price is not None else None,
            'discounted_price': float(p.discounted_price) if p.discounted_price is not None else None,
            'discount_percent': p.discount_percent,
            'avg_rating': p.avg_rating,
            'reviews_count': p.reviews.count(),
            'category': {'id': p.category.id, 'name': p.category.name, 'slug': p.category.slug} if p.category else None,
        } for p in products],
        'categories': [{
            'id': c.id,
            'name': c.name,
            'slug': c.slug,
            'image': c.image.url if c.image else None
        } for c in categories],
        'selected_category': {
            'id': selected_category.id,
            'name': selected_category.name,
            'slug': selected_category.slug
        } if selected_category else None
    })


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    reviews = product.reviews.all()
    related_products = Product.objects.filter(
        category=product.category, is_active=True
    ).exclude(id=product.id)[:4]

    if request.method == 'POST':
        import json
        try:
            data = json.loads(request.body)
        except Exception:
            data = request.POST
        rating = data.get('rating')
        comment = data.get('comment')
        if rating and comment:
            review, created = Review.objects.update_or_create(
                product=product,
                user=request.user if request.user.is_authenticated else None,
                defaults={'rating': int(rating), 'comment': comment}
            )
            return JsonResponse({'success': True, 'message': 'Review submitted successfully!'})
        return JsonResponse({'success': False, 'error': 'Missing parameters'})

    return JsonResponse({
        'success': True,
        'product': {
            'id': product.id,
            'name': product.name,
            'slug': product.slug,
            'description': product.description,
            'short_description': product.short_description,
            'price': float(product.price) if product.price is not None else None,
            'discounted_price': float(product.discounted_price) if product.discounted_price is not None else None,
            'discount_percent': product.discount_percent,
            'avg_rating': product.avg_rating,
            'wattage': product.wattage,
            'brand': product.brand,
            'warranty_years': product.warranty_years,
            'stock': product.stock,
            'image': product.image.url if product.image else None,
            'image2': product.image2.url if product.image2 else None,
            'image3': product.image3.url if product.image3 else None,
            'specifications': product.specifications
        },
        'reviews': [{
            'id': r.id,
            'display_name': r.display_name,
            'rating': r.rating,
            'comment': r.comment,
            'created_at': r.created_at.strftime('%d %b %Y')
        } for r in reviews],
        'related_products': [{
            'id': p.id,
            'name': p.name,
            'slug': p.slug,
            'image': p.image.url if p.image else None,
            'price': float(p.price) if p.price is not None else None,
            'discounted_price': float(p.discounted_price) if p.discounted_price is not None else None,
            'avg_rating': p.avg_rating
        } for p in related_products]
    })


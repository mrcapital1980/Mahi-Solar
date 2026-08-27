from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Product, Category, Review
from .serializers import ProductListSerializer, ProductSerializer, CategorySerializer, ReviewSerializer


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['request'] = self.request
        return ctx


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        return ProductSerializer

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['request'] = self.request
        return ctx

    def get_queryset(self):
        qs = super().get_queryset()
        category_slug = self.request.query_params.get('category')
        search = self.request.query_params.get('q', '')
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')

        if category_slug:
            qs = qs.filter(category__slug=category_slug)
        if search:
            qs = qs.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search) |
                Q(brand__icontains=search)
            )
        if min_price:
            qs = qs.filter(price__gte=min_price)
        if max_price:
            qs = qs.filter(price__lte=max_price)
        return qs

    @action(detail=False, methods=['get'])
    def featured(self, request):
        featured = self.get_queryset().filter(is_featured=True)[:6]
        serializer = ProductListSerializer(featured, many=True, context={'request': request})
        return Response({'success': True, 'featured_products': serializer.data})

    @action(detail=True, methods=['post'])
    def review(self, request, slug=None):
        product = self.get_object()
        user = request.user if request.user.is_authenticated else None
        data = request.data
        rating = data.get('rating')
        comment = data.get('comment')

        if not rating or not comment:
            return Response({'success': False, 'error': 'Missing rating or comment'}, status=400)

        review, created = Review.objects.update_or_create(
            product=product,
            user=user,
            defaults={'rating': int(rating), 'comment': comment}
        )
        serializer = ReviewSerializer(review)
        return Response({'success': True, 'review': serializer.data})

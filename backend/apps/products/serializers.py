from rest_framework import serializers
from .models import Category, Product, Review


class CategorySerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'image_url', 'is_active']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None


class ReviewSerializer(serializers.ModelSerializer):
    display_name = serializers.CharField(source='display_name', read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'display_name', 'rating', 'comment', 'created_at']


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    image_url = serializers.SerializerMethodField()
    image2_url = serializers.SerializerMethodField()
    image3_url = serializers.SerializerMethodField()
    effective_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    discount_percent = serializers.IntegerField(read_only=True)
    avg_rating = serializers.FloatField(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'short_description',
            'image_url', 'image2_url', 'image3_url',
            'price', 'discounted_price', 'effective_price', 'discount_percent',
            'wattage', 'brand', 'warranty_years', 'stock',
            'specifications', 'is_featured', 'avg_rating',
            'category', 'reviews', 'created_at',
        ]

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None

    def get_image2_url(self, obj):
        request = self.context.get('request')
        if obj.image2 and request:
            return request.build_absolute_uri(obj.image2.url)
        return None

    def get_image3_url(self, obj):
        request = self.context.get('request')
        if obj.image3 and request:
            return request.build_absolute_uri(obj.image3.url)
        return None


class ProductListSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    avg_rating = serializers.FloatField(read_only=True)
    discount_percent = serializers.IntegerField(read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'image_url', 'price', 'discounted_price',
            'discount_percent', 'avg_rating', 'wattage', 'brand',
            'is_featured', 'category', 'stock',
        ]

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None

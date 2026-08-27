from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Category, Product, Review


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ['is_active']
    search_fields = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'discounted_price', 'stock', 'is_active', 'is_featured']
    list_filter = ['category', 'is_active', 'is_featured', 'brand']
    search_fields = ['name', 'brand', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active', 'is_featured', 'stock']


# @admin.register(Review)
# class ReviewAdmin(admin.ModelAdmin):
#     list_display = ['user', 'product', 'rating', 'created_at']
#     list_filter = ['rating']
#     search_fields = ['user__username', 'product__name']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'product', 'rating', 'created_at']
    list_filter = ['rating']
    search_fields = ['name', 'user__username', 'product__name']

    def display_name(self, obj):
        return obj.display_name  # uses model logic

    display_name.short_description = 'User'
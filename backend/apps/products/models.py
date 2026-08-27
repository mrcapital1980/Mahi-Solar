from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

#
# class Product(models.Model):
#     WATTAGE_CHOICES = [
#         ('100W', '100W'), ('200W', '200W'), ('250W', '250W'),
#         ('300W', '300W'), ('350W', '350W'), ('400W', '400W'),
#         ('500W', '500W'), ('1KW', '1KW'), ('2KW', '2KW'),
#         ('3KW', '3KW'), ('5KW', '5KW'), ('10KW', '10KW'),
#     ]
#
#     category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
#     name = models.CharField(max_length=300)
#     slug = models.SlugField(unique=True, blank=True)
#     description = models.TextField()
#     short_description = models.CharField(max_length=500, blank=True)
#     price = models.DecimalField(max_digits=10, decimal_places=2)
#     discounted_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
#     wattage = models.CharField(max_length=20, choices=WATTAGE_CHOICES, blank=True)
#     brand = models.CharField(max_length=200, blank=True)
#     warranty_years = models.IntegerField(default=0)
#     stock = models.IntegerField(default=0)
#     is_active = models.BooleanField(default=True)
#     is_featured = models.BooleanField(default=False)
#     image = models.ImageField(upload_to='products/', blank=True, null=True)
#     image2 = models.ImageField(upload_to='products/', blank=True, null=True)
#     image3 = models.ImageField(upload_to='products/', blank=True, null=True)
#
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#
#     class Meta:
#         ordering = ['-created_at']
#
#     def save(self, *args, **kwargs):
#         if not self.slug:
#             self.slug = slugify(self.name)
#         super().save(*args, **kwargs)
#
#     def __str__(self):
#         return self.name
#
#     @property
#     def effective_price(self):
#         return self.discounted_price if self.discounted_price else self.price
#
#     @property
#     def discount_percent(self):
#         if self.discounted_price and self.price > 0:
#             return int(((self.price - self.discounted_price) / self.price) * 100)
#         return 0
#
#     @property
#     def avg_rating(self):
#         reviews = self.reviews.all()
#         if reviews.exists():
#             return round(sum(r.rating for r in reviews) / reviews.count(), 1)
#         return 0


# --> updated

class Product(models.Model):

    WATTAGE_CHOICES = [
        ('0W', '0W'), ('100W', '100W'), ('200W', '200W'), ('250W', '250W'),
        ('300W', '300W'), ('350W', '350W'), ('400W', '400W'),
        ('500W', '500W'), ('550W', '550W'), ('1KW', '1KW'), ('1.5KW', '1.5KW'), ('2KW', '2KW'),
        ('3KW', '3KW'), ('5KW', '5KW'), ('10KW', '10KW'),
    ]

    category = models.ForeignKey(
        'Category',
        on_delete=models.SET_NULL,
        null=True,
        related_name='products'
    )

    name = models.CharField(max_length=300)
    slug = models.SlugField(unique=True, blank=True)

    description = models.TextField()
    short_description = models.CharField(max_length=500, blank=True)

    # price = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discounted_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )

    wattage = models.CharField(
        max_length=20,
        choices=WATTAGE_CHOICES,
        blank=True
    )

    brand = models.CharField(max_length=200, blank=True)
    warranty_years = models.IntegerField(default=0)
    stock = models.IntegerField(default=0)

    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)

    image = models.ImageField(upload_to='products/', blank=True, null=True)
    image2 = models.ImageField(upload_to='products/', blank=True, null=True)
    image3 = models.ImageField(upload_to='products/', blank=True, null=True)

    specifications = models.JSONField(default=dict, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1

            while Product.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def effective_price(self):
        return self.discounted_price if self.discounted_price else self.price

    @property
    def discount_percent(self):
        if self.discounted_price and self.price and self.price > 0:
            return int(((self.price - self.discounted_price) / self.price) * 100)
        return 0

    @property
    def avg_rating(self):
        if hasattr(self, "reviews"):
            reviews = self.reviews.all()
            if reviews.exists():
                return round(sum(r.rating for r in reviews) / reviews.count(), 1)
        return 0


from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')

    # ✅ Make user optional (IMPORTANT CHANGE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    # ✅ Add manual name (NEW FIELD)
    name = models.CharField(max_length=100, null=True, blank=True)

    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # ❌ REMOVE unique_together (it will break manual reviews)
        ordering = ['-created_at']

    # ✅ Validation (SAFE)
    def clean(self):
        if not self.user and not self.name:
            raise ValidationError("Either select a user OR enter a name.")

        # Prevent duplicate reviews only for real users
        if self.user:
            existing = Review.objects.filter(product=self.product, user=self.user)
            if self.pk:
                existing = existing.exclude(pk=self.pk)
            if existing.exists():
                raise ValidationError("This user already reviewed this product.")

    # ✅ Ensure admin triggers validation
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    # ✅ SAFE display name (won’t break templates)
    @property
    def display_name(self):
        return self.user.username if self.user else self.name

    def __str__(self):
        return f"{self.display_name} - {self.product.name} ({self.rating}★)"


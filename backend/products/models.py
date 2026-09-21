

from django.db import models
from django.utils.text import slugify
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="categories/", blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products"
    )

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField()

    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )

    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to="products/", blank=True, null=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def discounted_price(self):
        discount = self.price * self.discount_percentage / 100
        return self.price - discount

    @property
    def approved_reviews(self):
        return self.reviews.filter(is_approved=True)

    @property
    def average_rating(self):
        avg = self.approved_reviews.aggregate(models.Avg('rating'))['rating__avg']
        return round(avg, 1) if avg else 0.0

    @property
    def review_count(self):
        return self.approved_reviews.count()

    @property
    def rating_breakdown(self):
        total = self.review_count
        approved = self.approved_reviews
        counts = {i: approved.filter(rating=i).count() for i in range(5, 0, -1)}
        percentages = {
            i: round((counts[i] / total * 100), 1) if total > 0 else 0
            for i in range(5, 0, -1)
        }
        return {
            'counts': counts,
            'percentages': percentages,
            'total': total,
        }

    def __str__(self):
        return self.name


class ProductReview(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="reviews"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="product_reviews"
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    review_text = models.TextField()
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("product", "user")
        verbose_name = "Product Review"
        verbose_name_plural = "Product Reviews"

    def __str__(self):
        return f"{self.product.name} - {self.user.username} ({self.rating}★)"


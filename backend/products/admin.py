

from django.contrib import admin
from .models import Category, Product, ProductReview


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "price",
        "discount_percentage",
        "stock",
        "is_active",
    )

    list_filter = (
        "category",
        "is_active",
    )

    search_fields = (
        "name",
        "description",
    )

    prepopulated_fields = {
        "slug": ("name",)
    }

    list_editable = (
        "price",
        "discount_percentage",
        "stock",
        "is_active",
    )


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "user",
        "rating",
        "is_approved",
        "created_at",
        "updated_at",
    )

    list_filter = (
        "is_approved",
        "rating",
        "created_at",
    )

    search_fields = (
        "product__name",
        "user__username",
        "user__email",
        "review_text",
    )

    list_editable = ("is_approved",)

    actions = ["approve_reviews", "unapprove_reviews"]

    @admin.action(description="Approve selected reviews")
    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)

    @admin.action(description="Unapprove selected reviews")
    def unapprove_reviews(self, request, queryset):
        queryset.update(is_approved=False)
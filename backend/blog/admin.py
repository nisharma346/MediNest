from django.contrib import admin

from .models import Article, ArticleCategory


@admin.register(ArticleCategory)
class ArticleCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "category",
        "author",
        "is_published",
        "is_featured",
        "published_date",
    )
    list_filter = ("is_published", "is_featured", "category")
    search_fields = ("title", "author", "short_description", "content")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ("Article", {
            "fields": (
                "title",
                "slug",
                "category",
                "author",
                "short_description",
                "content",
                "featured_image",
            )
        }),
        ("Publishing", {
            "fields": (
                "is_published",
                "is_featured",
                "published_date",
            )
        }),
        ("Metadata", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )

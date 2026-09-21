from django.contrib import admin
from .models import Service, Testimonial, HealthUpdate, GalleryItem


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "short_description",
        "is_active",
        "created_at",
    )

    list_filter = (
        "is_active",
    )

    search_fields = (
        "name",
        "short_description",
        "description",
    )

    list_editable = (
        "is_active",
    )


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "rating",
        "is_approved",
        "is_featured",
        "created_at",
    )

    list_filter = (
        "is_approved",
        "is_featured",
        "rating",
        "created_at",
    )

    search_fields = (
        "name",
        "message",
    )

    list_editable = (
        "is_approved",
        "is_featured",
    )

    ordering = (
        "-created_at",
    )

    actions = [
        "approve_testimonials",
        "unapprove_testimonials",
        "feature_testimonials",
        "unfeature_testimonials",
    ]

    @admin.action(description="Approve selected testimonials")
    def approve_testimonials(self, request, queryset):
        rows_updated = queryset.update(is_approved=True)
        self.message_user(request, f"{rows_updated} testimonial(s) approved successfully.")

    @admin.action(description="Unapprove selected testimonials")
    def unapprove_testimonials(self, request, queryset):
        rows_updated = queryset.update(is_approved=False)
        self.message_user(request, f"{rows_updated} testimonial(s) unapproved.")

    @admin.action(description="Mark selected testimonials as featured")
    def feature_testimonials(self, request, queryset):
        rows_updated = queryset.update(is_featured=True)
        self.message_user(request, f"{rows_updated} testimonial(s) marked as featured.")

    @admin.action(description="Remove featured status from selected testimonials")
    def unfeature_testimonials(self, request, queryset):
        rows_updated = queryset.update(is_featured=False)
        self.message_user(request, f"{rows_updated} testimonial(s) unfeatured.")


@admin.register(HealthUpdate)
class HealthUpdateAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "category",
        "published_date",
        "is_active",
        "is_featured",
        "created_at",
    )

    list_filter = (
        "is_active",
        "is_featured",
        "category",
        "published_date",
    )

    search_fields = (
        "title",
        "short_description",
        "content",
    )

    list_editable = (
        "is_active",
        "is_featured",
    )

    prepopulated_fields = {
        "slug": ("title",)
    }

    ordering = (
        "-published_date",
        "-created_at",
    )

    actions = [
        "make_active",
        "make_inactive",
        "make_featured",
        "unfeature",
    ]

    @admin.action(description="Mark selected updates as active")
    def make_active(self, request, queryset):
        rows_updated = queryset.update(is_active=True)
        self.message_user(request, f"{rows_updated} health update(s) published / set active.")

    @admin.action(description="Mark selected updates as inactive")
    def make_inactive(self, request, queryset):
        rows_updated = queryset.update(is_active=False)
        self.message_user(request, f"{rows_updated} health update(s) unpublished / set inactive.")

    @admin.action(description="Mark selected updates as featured")
    def make_featured(self, request, queryset):
        rows_updated = queryset.update(is_featured=True)
        self.message_user(request, f"{rows_updated} health update(s) marked as featured.")

    @admin.action(description="Remove featured status from selected updates")
    def unfeature(self, request, queryset):
        rows_updated = queryset.update(is_featured=False)
        self.message_user(request, f"{rows_updated} health update(s) unfeatured.")


@admin.register(GalleryItem)
class GalleryItemAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "category",
        "is_active",
        "is_featured",
        "created_at",
    )

    list_filter = (
        "is_active",
        "is_featured",
        "category",
        "created_at",
    )

    search_fields = (
        "title",
        "description",
    )

    list_editable = (
        "is_active",
        "is_featured",
    )

    ordering = (
        "-is_featured",
        "-created_at",
    )

    actions = [
        "make_active",
        "make_inactive",
        "make_featured",
        "unfeature",
    ]

    @admin.action(description="Mark selected gallery items as active")
    def make_active(self, request, queryset):
        rows_updated = queryset.update(is_active=True)
        self.message_user(request, f"{rows_updated} gallery item(s) published / set active.")

    @admin.action(description="Mark selected gallery items as inactive")
    def make_inactive(self, request, queryset):
        rows_updated = queryset.update(is_active=False)
        self.message_user(request, f"{rows_updated} gallery item(s) set inactive.")

    @admin.action(description="Mark selected gallery items as featured")
    def make_featured(self, request, queryset):
        rows_updated = queryset.update(is_featured=True)
        self.message_user(request, f"{rows_updated} gallery item(s) marked as featured.")

    @admin.action(description="Remove featured status from selected gallery items")
    def unfeature(self, request, queryset):
        rows_updated = queryset.update(is_featured=False)
        self.message_user(request, f"{rows_updated} gallery item(s) unfeatured.")




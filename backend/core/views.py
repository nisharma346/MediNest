import os
import urllib.parse
from pathlib import Path

import cloudinary
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Avg
from django.utils import timezone

from blog.models import Article
from products.models import Product, ProductReview
from doctors.models import Doctor
from appointments.models import Appointment
from orders.models import Order
from wishlist.models import WishlistItem
from .models import Service, Testimonial, HealthUpdate, GalleryItem, ContactMessage
from .forms import ContactForm


User = get_user_model()


def get_hero_image_url():
    try:
        hero_filename = "medinest_hero_image.png"
        cloudinary_url = getattr(settings, "CLOUDINARY_URL", None) or os.environ.get("CLOUDINARY_URL")
        if cloudinary_url:
            try:
                parsed = urllib.parse.urlparse(cloudinary_url)
                cloud_name = parsed.hostname
                if cloud_name:
                    return f"https://res.cloudinary.com/{cloud_name}/image/upload/{hero_filename}"
            except BaseException:
                pass

        local_root_path = Path(settings.MEDIA_ROOT) / hero_filename
        if local_root_path.exists():
            return f"{settings.MEDIA_URL}{hero_filename}"

        local_testimonials_path = Path(settings.MEDIA_ROOT) / "testimonials" / hero_filename
        if local_testimonials_path.exists():
            return f"{settings.MEDIA_URL}testimonials/{hero_filename}"

        return f"{settings.MEDIA_URL}{hero_filename}"
    except BaseException:
        return f"{settings.MEDIA_URL}medinest_hero_image.png"


def home(request):
    try:
        featured_products = Product.objects.filter(
            is_active=True
        ).select_related("category").order_by("-created_at")[:6]
    except BaseException:
        featured_products = []

    try:
        featured_doctors = Doctor.objects.filter(
            is_available=True
        ).order_by("name")[:4]
    except BaseException:
        featured_doctors = []

    try:
        services = Service.objects.filter(
            is_active=True
        ).order_by("name")[:6]
    except BaseException:
        services = []

    try:
        latest_articles = Article.objects.filter(
            is_published=True,
            published_date__lte=timezone.now(),
        ).select_related("category").order_by("-published_date", "-created_at")[:4]
    except BaseException:
        latest_articles = []

    try:
        testimonials = Testimonial.objects.filter(
            is_approved=True
        ).order_by("-is_featured", "-created_at")[:6]
    except BaseException:
        testimonials = []

    try:
        latest_updates = HealthUpdate.objects.filter(
            is_active=True,
            published_date__lte=timezone.now(),
        ).order_by("-is_featured", "-published_date")[:4]
    except BaseException:
        latest_updates = []

    try:
        gallery_items = GalleryItem.objects.filter(
            is_active=True
        ).order_by("-is_featured", "-created_at")[:6]
    except BaseException:
        gallery_items = []

    # Dynamic Statistics
    try:
        total_products_count = Product.objects.filter(is_active=True).count()
        total_doctors_count = Doctor.objects.filter(is_available=True).count()
        avg_rating_val = ProductReview.objects.filter(is_approved=True).aggregate(Avg("rating"))["rating__avg"]
        avg_patient_rating = round(avg_rating_val, 1) if avg_rating_val else 4.9
    except BaseException:
        total_products_count = 10
        total_doctors_count = 8
        avg_patient_rating = 4.9

    # Wishlist IDs for authenticated users
    wishlist_ids = set()
    try:
        if hasattr(request, "user") and request.user.is_authenticated:
            wishlist_ids = set(
                WishlistItem.objects.filter(user=request.user).values_list("product_id", flat=True)
            )
    except BaseException:
        pass

    hero_image_url = get_hero_image_url()

    return render(
        request,
        "core/home.html",
        {
            "featured_products": featured_products,
            "featured_doctors": featured_doctors,
            "services": services,
            "latest_articles": latest_articles,
            "testimonials": testimonials,
            "latest_updates": latest_updates,
            "gallery_items": gallery_items,
            "total_products_count": total_products_count,
            "total_doctors_count": total_doctors_count,
            "avg_patient_rating": avg_patient_rating,
            "wishlist_ids": wishlist_ids,
            "hero_image_url": hero_image_url,
        }
    )


def gallery_list(request):
    category = request.GET.get("category", "").strip()
    items = GalleryItem.objects.filter(is_active=True)
    if category:
        items = items.filter(category=category)
    items = items.order_by("-is_featured", "-created_at")

    categories = GalleryItem.CATEGORY_CHOICES

    return render(
        request,
        "core/gallery_list.html",
        {
            "items": items,
            "categories": categories,
            "selected_category": category,
        }
    )



def health_update_list(request):
    category = request.GET.get("category", "").strip()
    updates = HealthUpdate.objects.filter(
        is_active=True,
        published_date__lte=timezone.now(),
    )
    if category:
        updates = updates.filter(category=category)
    updates = updates.order_by("-is_featured", "-published_date")

    categories = HealthUpdate.CATEGORY_CHOICES

    return render(
        request,
        "core/health_update_list.html",
        {
            "updates": updates,
            "categories": categories,
            "selected_category": category,
        }
    )


def health_update_detail(request, slug):
    update = get_object_or_404(
        HealthUpdate,
        slug=slug,
        is_active=True,
        published_date__lte=timezone.now(),
    )
    recent_updates = HealthUpdate.objects.filter(
        is_active=True,
        published_date__lte=timezone.now(),
    ).exclude(pk=update.pk).order_by("-published_date")[:5]

    return render(
        request,
        "core/health_update_detail.html",
        {
            "update": update,
            "recent_updates": recent_updates,
        }
    )


def services(request):
    services = Service.objects.filter(
        is_active=True
    ).order_by("name")

    return render(
        request,
        "core/services.html",
        {"services": services}
    )


def service_detail(request, pk):
    service = get_object_or_404(Service, pk=pk, is_active=True)
    other_services = Service.objects.filter(
        is_active=True
    ).exclude(pk=pk).order_by("name")[:4]

    return render(
        request,
        "core/service_detail.html",
        {
            "service": service,
            "other_services": other_services,
        }
    )



def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Thank you for contacting MediNest. Our team will get back to you soon."
            )
            return redirect("core:contact")
        else:
            messages.error(
                request,
                "Please fix the validation errors below."
            )
    else:
        form = ContactForm()

    return render(
        request,
        "core/contact.html",
        {"form": form}
    )




@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        return render(
            request,
            "core/admin_dashboard_forbidden.html",
            {"message": "Access Denied: You do not have staff permissions to view the Admin Dashboard."},
            status=403
        )

    # 1. Statistics Cards
    total_products = Product.objects.count()
    active_products = Product.objects.filter(is_active=True).count()
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status="pending").count()
    total_users = User.objects.count()
    total_doctors = Doctor.objects.count()
    total_appointments = Appointment.objects.count()
    pending_appointments = Appointment.objects.filter(status="Pending").count()
    total_articles = Article.objects.count()
    total_reviews = ProductReview.objects.count()

    # 2. Sales Summary
    now = timezone.now()
    today = now.date()

    total_sales = Order.objects.exclude(status="cancelled").aggregate(
        total=Sum("total_amount")
    )["total"] or 0

    today_orders = Order.objects.filter(created_at__date=today).count()
    today_sales = Order.objects.filter(created_at__date=today).exclude(status="cancelled").aggregate(
        total=Sum("total_amount")
    )["total"] or 0

    month_orders = Order.objects.filter(created_at__year=now.year, created_at__month=now.month).count()
    month_sales = Order.objects.filter(created_at__year=now.year, created_at__month=now.month).exclude(status="cancelled").aggregate(
        total=Sum("total_amount")
    )["total"] or 0

    # 3. Recent Items
    recent_orders = Order.objects.select_related("user").order_by("-created_at")[:5]
    recent_appointments = Appointment.objects.select_related("user", "doctor").order_by("-created_at")[:5]
    low_stock_products = Product.objects.filter(stock__lte=5, is_active=True).select_related("category").order_by("stock")[:5]
    recent_reviews = ProductReview.objects.select_related("product", "user").order_by("-created_at")[:5]

    context = {
        "total_products": total_products,
        "active_products": active_products,
        "total_orders": total_orders,
        "pending_orders": pending_orders,
        "total_users": total_users,
        "total_doctors": total_doctors,
        "total_appointments": total_appointments,
        "pending_appointments": pending_appointments,
        "total_articles": total_articles,
        "total_reviews": total_reviews,
        "total_sales": total_sales,
        "today_orders": today_orders,
        "today_sales": today_sales,
        "month_orders": month_orders,
        "month_sales": month_sales,
        "recent_orders": recent_orders,
        "recent_appointments": recent_appointments,
        "low_stock_products": low_stock_products,
        "recent_reviews": recent_reviews,
    }

    return render(request, "core/admin_dashboard.html", context)
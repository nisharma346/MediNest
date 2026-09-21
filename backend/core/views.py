from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.utils import timezone

from blog.models import Article
from products.models import Product, ProductReview
from doctors.models import Doctor
from appointments.models import Appointment
from orders.models import Order
from .models import Service

User = get_user_model()


def home(request):
    featured_products = Product.objects.filter(
        is_active=True
    ).order_by("-created_at")[:6]

    featured_doctors = Doctor.objects.filter(
        is_available=True
    ).order_by("name")[:4]

    services = Service.objects.filter(
        is_active=True
    ).order_by("name")[:6]

    latest_articles = Article.objects.filter(
        is_published=True
    ).order_by("-published_date", "-created_at")[:4]

    return render(
        request,
        "core/home.html",
        {
            "featured_products": featured_products,
            "featured_doctors": featured_doctors,
            "services": services,
            "latest_articles": latest_articles,
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
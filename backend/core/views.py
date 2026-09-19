from django.shortcuts import render

from products.models import Product
from doctors.models import Doctor
from .models import Service


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

    return render(
        request,
        "core/home.html",
        {
            "featured_products": featured_products,
            "featured_doctors": featured_doctors,
            "services": services,
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
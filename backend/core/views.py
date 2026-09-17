
from django.shortcuts import render
from products.models import Product


def home(request):
    featured_products = Product.objects.filter(
        is_active=True
    ).order_by("-created_at")[:6]

    return render(
        request,
        "core/home.html",
        {
            "featured_products": featured_products
        }
    )
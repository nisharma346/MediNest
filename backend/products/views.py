

from django.shortcuts import render
from .models import Product


def product_list(request):
    products = Product.objects.filter(is_active=True).select_related("category")

    return render(
        request,
        "products/product_list.html",
        {"products": products}
    )
from django.shortcuts import render, get_object_or_404
from .models import Product


def product_list(request):
    products = Product.objects.filter(
        is_active=True
    ).select_related("category")

    return render(
        request,
        "products/product_list.html",
        {"products": products}
    )


def product_detail(request, slug):
    product = get_object_or_404(
        Product,
        slug=slug,
        is_active=True
    )

    return render(
        request,
        "products/product_detail.html",
        {"product": product}
    )

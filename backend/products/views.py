

from django.shortcuts import render
from .models import Product


def product_list(request):
    products = Product.objects.filter(is_active=True).select_related("category")

    return render(
        request,
        "products/product_list.html",
        {"products": products}
    )

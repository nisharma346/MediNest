from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from cart.views import add_to_cart as add_product_to_cart
from products.models import Product
from .models import WishlistItem


@login_required(login_url="accounts:login")
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if not product.is_active:
        raise Http404("This product is no longer available.")

    if product.stock <= 0:
        messages.error(request, f"{product.name} is currently out of stock.")
        return render(
            request,
            "products/product_detail.html",
            {
                "product": product,
                "in_wishlist": WishlistItem.objects.filter(user=request.user, product=product).exists(),
                "message": "This product is out of stock."
            }
        )

    item, created = WishlistItem.objects.get_or_create(user=request.user, product=product)

    if created:
        messages.success(request, f"{product.name} was added to your wishlist.")
    else:
        messages.info(request, f"{product.name} is already in your wishlist.")

    next_url = request.POST.get("next") or request.GET.get("next")
    if next_url:
        return redirect(next_url)

    if request.META.get("HTTP_REFERER"):
        return redirect(request.META.get("HTTP_REFERER"))

    return redirect("products:product_list")


@login_required(login_url="accounts:login")
def wishlist(request):
    wishlist_items = WishlistItem.objects.filter(user=request.user).select_related("product", "product__category")

    return render(
        request,
        "wishlist/wishlist.html",
        {"wishlist_items": wishlist_items}
    )


@login_required(login_url="accounts:login")
def remove_from_wishlist(request, product_id):
    item = get_object_or_404(WishlistItem, user=request.user, product_id=product_id)
    product_name = item.product.name
    item.delete()
    messages.success(request, f"{product_name} was removed from your wishlist.")
    return redirect("wishlist:wishlist")


@login_required(login_url="accounts:login")
def add_to_cart_from_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    if product.stock <= 0:
        messages.error(request, f"{product.name} is currently out of stock.")
        return redirect("wishlist:wishlist")

    response = add_product_to_cart(request, product_id)
    return response

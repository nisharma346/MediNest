from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from products.models import Product
from .models import CartItem


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(
        Product,
        id=product_id,
        is_active=True
    )

    cart_item, created = CartItem.objects.get_or_create(
        user=request.user,
        product=product
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect("cart:cart_detail")


@login_required
def cart_detail(request):
    cart_items = CartItem.objects.filter(
        user=request.user
    ).select_related("product", "product__category")

    total = sum(
        item.subtotal for item in cart_items
    )

    return render(
        request,
        "cart/cart_detail.html",
        {
            "cart_items": cart_items,
            "total": total,
        }
    )


@login_required
def increase_quantity(request, item_id):
    cart_item = get_object_or_404(
        CartItem,
        id=item_id,
        user=request.user
    )

    cart_item.quantity += 1
    cart_item.save()

    return redirect("cart:cart_detail")


@login_required
def decrease_quantity(request, item_id):
    cart_item = get_object_or_404(
        CartItem,
        id=item_id,
        user=request.user
    )

    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()

    return redirect("cart:cart_detail")


@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(
        CartItem,
        id=item_id,
        user=request.user
    )

    cart_item.delete()

    return redirect("cart:cart_detail")
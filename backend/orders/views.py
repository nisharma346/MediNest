import hashlib
import hmac
import razorpay


from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from cart.models import CartItem
from .models import Order, OrderItem


try:
    import razorpay
except ImportError:  # pragma: no cover
    razorpay = None


def _generate_invoice_number(order):
    timestamp = timezone.now().strftime("%Y%m%d")
    return f"MEDI-{timestamp}-{order.id:05d}"


def _verify_razorpay_signature(razorpay_order_id, payment_id, signature):
    if not settings.RAZORPAY_KEY_SECRET:
        return False

    payload = f"{razorpay_order_id}|{payment_id}".encode()
    expected = hmac.new(
        settings.RAZORPAY_KEY_SECRET.encode(),
        payload,
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(expected, signature)


@login_required
def checkout(request):

    cart_items = CartItem.objects.filter(
        user=request.user
    ).select_related("product", "product__category")

    if not cart_items.exists():
        return redirect("cart:cart_detail")

    total = sum(
        item.subtotal for item in cart_items
    )

    if request.method == "POST":

        full_name = request.POST.get("full_name")
        phone = request.POST.get("phone")

        address_line1 = request.POST.get("address_line1")
        address_line2 = request.POST.get("address_line2")

        city = request.POST.get("city")
        state = request.POST.get("state")
        pincode = request.POST.get("pincode")

        payment_method = request.POST.get(
            "payment_method",
            "cod"
        )

        order = Order.objects.create(
            user=request.user,
            full_name=full_name,
            phone=phone,
            address_line1=address_line1,
            address_line2=address_line2,
            city=city,
            state=state,
            pincode=pincode,
            payment_method=payment_method,
            total_amount=total,
        )

        for item in cart_items:

            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.discounted_price
            )

        if payment_method == "razorpay":
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                if razorpay is None:
                    return JsonResponse(
                        {"success": False, "message": "Razorpay package is not installed."},
                        status=400,
                    )

                if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
                    return JsonResponse(
                        {"success": False, "message": "Razorpay is not configured yet."},
                        status=400,
                    )

                client = razorpay.Client(
                    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
                )

                try:
                    razorpay_order = client.order.create(
                        data={
                            "amount": int(total * 100),
                            "currency": "INR",
                            "receipt": f"order_{order.id}",
                            "notes": {
                                "order_id": str(order.id),
                                "customer": full_name,
                            },
                        }
                    )
                except Exception as exc:  # pragma: no cover
                    return JsonResponse(
                        {"success": False, "message": f"Razorpay payment setup failed: {exc}"},
                        status=400,
                    )

                order.razorpay_order_id = razorpay_order.get("id")
                order.save(update_fields=["razorpay_order_id"])

                return JsonResponse(
                    {
                        "success": True,
                        "order_id": order.id,
                        "razorpay_order_id": order.razorpay_order_id,
                        "amount": int(total * 100),
                        "currency": "INR",
                        "key": settings.RAZORPAY_KEY_ID,
                    }
                )

            return redirect("orders:checkout")

        order.status = "confirmed"
        order.invoice_number = order.invoice_number or _generate_invoice_number(order)
        order.paid_at = timezone.now()
        order.save(update_fields=["status", "invoice_number", "paid_at"])

        # Cart clear
        cart_items.delete()

        return redirect(
            "orders:order_success",
            order_id=order.id
        )

    return render(
        request,
        "orders/checkout.html",
        {
            "cart_items": cart_items,
            "total": total,
        }
    )


@login_required
@require_POST
def payment_callback(request):
    local_order_id = request.POST.get("local_order_id") or request.POST.get("order_id")
    payment_id = request.POST.get("payment_id")
    razorpay_order_id = request.POST.get("razorpay_order_id")
    signature = request.POST.get("signature")

    if not local_order_id or not payment_id or not razorpay_order_id or not signature:
        return JsonResponse(
            {"success": False, "message": "Payment callback data is incomplete."},
            status=400,
        )

    order = get_object_or_404(Order, id=local_order_id, user=request.user)

    if order.status == "cancelled":
        return JsonResponse(
            {"success": False, "message": "Cancelled orders cannot be processed for payment."},
            status=400,
        )

    if order.razorpay_order_id and order.razorpay_order_id != razorpay_order_id:
        return JsonResponse(
            {"success": False, "message": "Razorpay order ID mismatch."},
            status=400,
        )

    if not _verify_razorpay_signature(razorpay_order_id, payment_id, signature):
        return JsonResponse(
            {"success": False, "message": "Payment verification failed."},
            status=400,
        )

    order.status = "confirmed"
    order.razorpay_payment_id = payment_id
    order.razorpay_signature = signature
    order.paid_at = timezone.now()
    order.invoice_number = order.invoice_number or _generate_invoice_number(order)
    order.save(
        update_fields=[
            "status",
            "razorpay_payment_id",
            "razorpay_signature",
            "paid_at",
            "invoice_number",
        ]
    )

    CartItem.objects.filter(user=request.user).delete()

    return JsonResponse(
        {
            "success": True,
            "redirect_url": reverse("orders:order_success", args=[order.id]),
        }
    )



@login_required
def order_success(request, order_id):
    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    if not order.invoice_number:
        order.invoice_number = _generate_invoice_number(order)
        order.save(update_fields=["invoice_number"])

    return render(
        request,
        "orders/order_success.html",
        {
            "order": order,
        }
    )


@login_required
def invoice(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if not order.invoice_number:
        order.invoice_number = _generate_invoice_number(order)
        order.save(update_fields=["invoice_number"])

    return render(
        request,
        "orders/invoice.html",
        {"order": order},
    )


@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by("-created_at")
    return render(
        request,
        "orders/my_orders.html",
        {"orders": orders},
    )


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(
        request,
        "orders/order_detail.html",
        {"order": order},
    )
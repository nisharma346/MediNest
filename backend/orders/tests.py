import hashlib
import hmac

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from cart.models import CartItem
from orders.models import Order
from products.models import Category, Product


class RazorpayInvoiceFlowTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="demo",
            email="demo@example.com",
            password="strongpass123"
        )
        self.client.force_login(self.user)

        category = Category.objects.create(name="Supplements", slug="supplements")
        self.product = Product.objects.create(
            category=category,
            name="Vitamin C",
            slug="vitamin-c",
            description="Good health",
            price=799.00,
            discount_percentage=0,
            stock=10,
        )

        self.cart_item = CartItem.objects.create(
            user=self.user,
            product=self.product,
            quantity=2,
        )

    def test_payment_callback_marks_order_paid_and_generates_invoice(self):
        order = Order.objects.create(
            user=self.user,
            full_name="Demo User",
            phone="9876543210",
            address_line1="123 Main St",
            city="Bengaluru",
            state="Karnataka",
            pincode="560001",
            payment_method="razorpay",
            total_amount=1598.00,
            razorpay_order_id="order_123",
        )

        payment_id = "pay_456"
        payload = f"{order.razorpay_order_id}|{payment_id}".encode()
        secret = "test_secret"
        signature = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()

        with self.settings(RAZORPAY_KEY_SECRET="test_secret"):
            response = self.client.post(
                reverse("orders:payment_callback"),
                data={
                    "order_id": order.razorpay_order_id,
                    "payment_id": payment_id,
                    "signature": signature,
                    "local_order_id": order.id,
                },
                content_type="application/json",
            )

        order.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(order.status, "confirmed")
        self.assertEqual(order.razorpay_payment_id, payment_id)
        self.assertTrue(order.invoice_number)
        self.assertTrue(CartItem.objects.filter(user=self.user).count() == 0)

from django.urls import path

from .views import checkout, order_success, payment_callback, invoice


app_name = "orders"


urlpatterns = [

    path(
        "checkout/",
        checkout,
        name="checkout"
    ),

    path(
        "payment/callback/",
        payment_callback,
        name="payment_callback"
    ),

    path(
        "invoice/<int:order_id>/",
        invoice,
        name="invoice"
    ),

    path(
        "success/<int:order_id>/",
        order_success,
        name="order_success"
    ),

]
from django.urls import path

from .views import (
    checkout,
    order_success,
    payment_callback,
    invoice,
    my_orders,
    order_detail,
)


app_name = "orders"


urlpatterns = [

    path(
        "my-orders/",
        my_orders,
        name="my_orders"
    ),

    path(
        "detail/<int:order_id>/",
        order_detail,
        name="order_detail"
    ),

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
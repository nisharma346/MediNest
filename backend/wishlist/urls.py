from django.urls import path

from .views import add_to_wishlist, wishlist, remove_from_wishlist, add_to_cart_from_wishlist

app_name = "wishlist"

urlpatterns = [
    path("", wishlist, name="wishlist"),
    path("add/<int:product_id>/", add_to_wishlist, name="add_to_wishlist"),
    path("remove/<int:product_id>/", remove_from_wishlist, name="remove_from_wishlist"),
    path("cart/add/<int:product_id>/", add_to_cart_from_wishlist, name="add_to_cart_from_wishlist"),
]

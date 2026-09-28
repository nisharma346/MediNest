from django.contrib import admin
from .models import CartItem


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "product", "quantity", "added_at")
    search_fields = ("user__username", "product__name")
    list_filter = ("added_at",)

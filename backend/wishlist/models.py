from django.conf import settings
from django.db import models

from products.models import Product


class WishlistItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'product'], name='unique_wishlist_user_product')
        ]

    def __str__(self):
        return f"{self.user} - {self.product.name}"

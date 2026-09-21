from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from products.models import Category, Product
from wishlist.models import WishlistItem


class WishlistFlowTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='alice',
            email='alice@example.com',
            password='secret123'
        )
        self.other_user = get_user_model().objects.create_user(
            username='bob',
            email='bob@example.com',
            password='secret123'
        )
        self.category = Category.objects.create(name='Supplements', slug='supplements')
        self.product = Product.objects.create(
            category=self.category,
            name='Vitamin C',
            slug='vitamin-c',
            description='Daily immune support.',
            price=500,
            discount_percentage=10,
            stock=20,
            is_active=True,
        )

    def test_add_to_wishlist_and_duplicate_prevented(self):
        self.client.login(username='alice', password='secret123')
        response = self.client.post(reverse('wishlist:add_to_wishlist', args=[self.product.id]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(WishlistItem.objects.filter(user=self.user, product=self.product).count(), 1)

        response = self.client.post(reverse('wishlist:add_to_wishlist', args=[self.product.id]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(WishlistItem.objects.filter(user=self.user, product=self.product).count(), 1)

    def test_wishlist_page_and_remove_from_wishlist(self):
        self.client.login(username='alice', password='secret123')
        WishlistItem.objects.create(user=self.user, product=self.product)

        response = self.client.get(reverse('wishlist:wishlist'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.name)

        response = self.client.post(reverse('wishlist:remove_from_wishlist', args=[self.product.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(WishlistItem.objects.filter(user=self.user, product=self.product).exists())

    def test_add_to_cart_from_wishlist(self):
        self.client.login(username='alice', password='secret123')
        WishlistItem.objects.create(user=self.user, product=self.product)

        response = self.client.post(reverse('wishlist:add_to_cart_from_wishlist', args=[self.product.id]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.user.cartitem_set.filter(product=self.product).exists())

    def test_logged_out_user_redirected_to_login(self):
        response = self.client.post(reverse('wishlist:add_to_wishlist', args=[self.product.id]))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_other_users_cannot_see_each_others_wishlist(self):
        WishlistItem.objects.create(user=self.user, product=self.product)
        self.client.login(username='bob', password='secret123')

        response = self.client.get(reverse('wishlist:wishlist'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, self.product.name)

    def test_inactive_or_out_of_stock_product_is_rejected(self):
        self.product.is_active = False
        self.product.save()

        self.client.login(username='alice', password='secret123')
        response = self.client.post(reverse('wishlist:add_to_wishlist', args=[self.product.id]))
        self.assertEqual(response.status_code, 404)

        self.product.is_active = True
        self.product.stock = 0
        self.product.save()

        response = self.client.post(reverse('wishlist:add_to_wishlist', args=[self.product.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'out of stock', status_code=200)

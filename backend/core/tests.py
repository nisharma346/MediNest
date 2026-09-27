from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from blog.models import Article, ArticleCategory
from doctors.models import Doctor
from .models import GalleryItem, HealthUpdate


class PublicHomeVisibilityTests(TestCase):
    def setUp(self):
        self.category = ArticleCategory.objects.create(
            name="Wellness",
            slug="wellness",
            is_active=True,
        )

        self.hidden_article = Article.objects.create(
            title="Draft Article Hidden From Homepage",
            slug="draft-article-hidden-from-homepage",
            short_description="Should not appear publicly.",
            content="Hidden draft content.",
            category=self.category,
            author="MediNest Team",
            is_published=False,
            published_date=timezone.now(),
        )

        self.hidden_doctor = Doctor.objects.create(
            name="Dr. Hidden Doctor",
            specialization="General Physician",
            qualification="MBBS, MD",
            experience=5,
            consultation_fee=500.00,
            available_days="Monday",
            available_time="10:00 AM - 12:00 PM",
            is_available=False,
        )

        self.hidden_update = HealthUpdate.objects.create(
            title="Draft Internal Notice",
            slug="draft-internal-notice",
            short_description="Hidden from public view.",
            content="Not published.",
            category="MediNest Updates",
            published_date=timezone.now(),
            is_active=False,
        )

        self.hidden_gallery_item = GalleryItem.objects.create(
            title="Private Draft Photo",
            image="gallery/private.jpg",
            description="Hidden gallery item.",
            category="MediNest",
            is_active=False,
        )

    def test_homepage_does_not_show_hidden_content(self):
        response = self.client.get(reverse("core:home"))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, self.hidden_article.title)
        self.assertNotContains(response, self.hidden_doctor.name)
        self.assertNotContains(response, self.hidden_update.title)
        self.assertNotContains(response, self.hidden_gallery_item.title)

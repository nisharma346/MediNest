from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from blog.models import Article, ArticleCategory


class ArticleVisibilityTests(TestCase):
    def setUp(self):
        self.category = ArticleCategory.objects.create(
            name="General Health",
            slug="general-health",
            description="General wellness advice",
            is_active=True,
        )

        self.published_article = Article.objects.create(
            title="Healthy Habits for Daily Life",
            slug="healthy-habits-for-daily-life",
            short_description="Simple wellness habits to follow every day.",
            content="This is the full published article content.",
            category=self.category,
            author="MediNest Team",
            is_published=True,
            is_featured=True,
        )

        self.draft_article = Article.objects.create(
            title="Draft Article Hidden From Public",
            slug="draft-article-hidden-from-public",
            short_description="This should not be visible publicly.",
            content="Draft content that should stay hidden.",
            category=self.category,
            author="MediNest Team",
            is_published=False,
            is_featured=False,
        )

    def test_blog_listing_shows_only_published_articles(self):
        response = self.client.get(reverse("blog:article_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.published_article.title)
        self.assertNotContains(response, self.draft_article.title)

    def test_article_detail_requires_published_article(self):
        published_response = self.client.get(reverse("blog:article_detail", args=[self.published_article.slug]))
        self.assertEqual(published_response.status_code, 200)

        draft_response = self.client.get(reverse("blog:article_detail", args=[self.draft_article.slug]))
        self.assertEqual(draft_response.status_code, 404)

    def test_future_dated_articles_are_hidden_from_public_pages(self):
        future_article = Article.objects.create(
            title="Future Article Not Yet Visible",
            slug="future-article-not-yet-visible",
            short_description="This should remain hidden until its publish date arrives.",
            content="Future published content should not appear on the public site yet.",
            category=self.category,
            author="MediNest Team",
            is_published=True,
            published_date=timezone.now() + timedelta(days=1),
            is_featured=False,
        )

        listing_response = self.client.get(reverse("blog:article_list"))
        self.assertNotContains(listing_response, future_article.title)

        detail_response = self.client.get(reverse("blog:article_detail", args=[future_article.slug]))
        self.assertEqual(detail_response.status_code, 404)

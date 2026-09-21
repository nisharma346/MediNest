from django.db import models
from django.utils import timezone
from django.utils.text import slugify


class ArticleCategory(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=150, unique=True, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Article Category"
        verbose_name_plural = "Article Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Article(models.Model):
    category = models.ForeignKey(
        ArticleCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="articles"
    )
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    short_description = models.CharField(max_length=255)
    content = models.TextField()
    featured_image = models.ImageField(upload_to="blog/", blank=True, null=True)
    author = models.CharField(max_length=120, default="MediNest Editorial Team")
    published_date = models.DateTimeField(default=timezone.now)
    is_published = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-published_date", "-created_at"]
        verbose_name = "Article"
        verbose_name_plural = "Articles"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            self.slug = base_slug

        if self.slug:
            base_slug = self.slug
            candidate = base_slug
            counter = 1
            while Article.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                candidate = f"{base_slug}-{counter}"
                counter += 1
            self.slug = candidate

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

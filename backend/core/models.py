from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.utils.text import slugify


class Service(models.Model):
    name = models.CharField(max_length=150)

    short_description = models.CharField(max_length=250)

    description = models.TextField()

    icon = models.CharField(
        max_length=100,
        blank=True,
        help_text="Example: fa-solid fa-heart-pulse"
    )

    image = models.ImageField(
        upload_to="services/",
        blank=True,
        null=True,
        max_length=255
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Testimonial(models.Model):
    name = models.CharField(max_length=100)

    profile_image = models.ImageField(
        upload_to="testimonials/",
        blank=True,
        null=True,
        max_length=255
    )

    rating = models.PositiveSmallIntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5"
    )

    message = models.TextField()

    is_approved = models.BooleanField(
        default=True,
        help_text="Designates whether this testimonial is published on the website."
    )

    is_featured = models.BooleanField(
        default=False,
        help_text="Designates whether this testimonial is highlighted on the homepage."
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-is_featured", "-created_at"]

    def __str__(self):
        return f"{self.name} ({self.rating}/5)"


class HealthUpdate(models.Model):
    CATEGORY_CHOICES = (
        ("General Health", "General Health"),
        ("Health Awareness", "Health Awareness"),
        ("Nutrition", "Nutrition"),
        ("Wellness", "Wellness"),
        ("Preventive Care", "Preventive Care"),
        ("MediNest Updates", "MediNest Updates"),
    )

    title = models.CharField(max_length=200)

    slug = models.SlugField(
        max_length=220,
        unique=True,
        blank=True,
        help_text="Unique URL identifier automatically generated from title."
    )

    short_description = models.CharField(
        max_length=255,
        help_text="Brief summary shown on update cards."
    )

    content = models.TextField(
        help_text="Full update / announcement content."
    )

    image = models.ImageField(
        upload_to="health_updates/",
        blank=True,
        null=True,
        max_length=255,
        help_text="Optional header / announcement image."
    )

    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default="General Health"
    )

    published_date = models.DateTimeField(default=timezone.now)

    is_active = models.BooleanField(
        default=True,
        help_text="Designates whether this update is visible to the public."
    )

    is_featured = models.BooleanField(
        default=False,
        help_text="Designates whether this update is highlighted on the homepage."
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_featured", "-published_date", "-created_at"]
        verbose_name = "Health Update / Announcement"
        verbose_name_plural = "Health Updates & Announcements"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            self.slug = base_slug

        if self.slug:
            base_slug = self.slug
            candidate = base_slug
            counter = 1
            while HealthUpdate.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                candidate = f"{base_slug}-{counter}"
                counter += 1
            self.slug = candidate

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class GalleryItem(models.Model):
    CATEGORY_CHOICES = (
        ("Healthcare", "Healthcare"),
        ("Wellness", "Wellness"),
        ("Doctors", "Doctors"),
        ("Awareness", "Awareness"),
        ("Events", "Events"),
        ("MediNest", "MediNest"),
    )

    title = models.CharField(max_length=200)

    image = models.ImageField(
        upload_to="gallery/",
        max_length=255,
        help_text="Gallery photo / image file."
    )

    description = models.TextField(
        blank=True,
        help_text="Optional caption or details for the photo."
    )

    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default="Healthcare"
    )

    is_active = models.BooleanField(
        default=True,
        help_text="Designates whether this media item is visible in the public gallery."
    )

    is_featured = models.BooleanField(
        default=False,
        help_text="Designates whether this media item is highlighted on the homepage."
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-is_featured", "-created_at"]
        verbose_name = "Gallery Item"
        verbose_name_plural = "Gallery Items"

    def __str__(self):
        return f"{self.title} ({self.category})"


class ContactMessage(models.Model):
    STATUS_CHOICES = (
        ("New", "New"),
        ("Read", "Read"),
        ("Replied", "Replied"),
    )

    name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, default="")
    subject = models.CharField(max_length=200)
    message = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="New"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Contact Message"
        verbose_name_plural = "Contact Messages"

    def __str__(self):
        return f"{self.subject} - {self.name} ({self.status})"




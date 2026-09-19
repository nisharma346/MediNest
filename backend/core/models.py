from django.db import models

from django.db import models


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
        null=True
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
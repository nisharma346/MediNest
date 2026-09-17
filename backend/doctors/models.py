from django.db import models


class Doctor(models.Model):
    SPECIALIZATION_CHOICES = [
        ("General Physician", "General Physician"),
        ("Cardiologist", "Cardiologist"),
        ("Dermatologist", "Dermatologist"),
        ("Dentist", "Dentist"),
        ("Pediatrician", "Pediatrician"),
        ("Gynecologist", "Gynecologist"),
        ("Neurologist", "Neurologist"),
        ("Orthopedic", "Orthopedic"),
    ]

    name = models.CharField(max_length=150)

    specialization = models.CharField(
        max_length=100,
        choices=SPECIALIZATION_CHOICES
    )

    qualification = models.CharField(max_length=200)

    experience = models.PositiveIntegerField(
        help_text="Experience in years"
    )

    bio = models.TextField(blank=True)

    profile_image = models.ImageField(
        upload_to="doctors/",
        blank=True,
        null=True
    )

    consultation_fee = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )

    available_days = models.CharField(
        max_length=200,
        help_text="Example: Monday, Wednesday, Friday"
    )

    available_time = models.CharField(
        max_length=100,
        help_text="Example: 10:00 AM - 2:00 PM"
    )

    is_available = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
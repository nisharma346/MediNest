import re
from datetime import datetime

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
        null=True,
        max_length=255
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

    @property
    def display_name(self):
        name = (self.name or "").strip()
        if not name:
            return "Dr."

        normalized_name = re.sub(r"^(?:Dr\.\s*)+", "", name, flags=re.IGNORECASE)
        normalized_name = normalized_name.strip()

        if not normalized_name:
            return "Dr."

        return f"Dr. {normalized_name}"

    def get_available_time_range(self):
        if not self.available_time:
            return None, None

        time_range = self.available_time.strip()
        if not time_range:
            return None, None

        split_pattern = r"\s*(?:-|to|–)\s*"
        parts = [part.strip() for part in re.split(split_pattern, time_range, flags=re.IGNORECASE)]
        if len(parts) != 2:
            return None, None

        start_raw, end_raw = parts

        time_formats = [
            "%I:%M %p",
            "%I %p",
            "%H:%M",
            "%I:%M:%S %p",
            "%I:%M:%S",
        ]

        def parse_single(value):
            cleaned = (value or "").strip()
            for fmt in time_formats:
                try:
                    return datetime.strptime(cleaned, fmt).time()
                except ValueError:
                    continue
            return None

        start_time = parse_single(start_raw)
        end_time = parse_single(end_raw)

        if start_time is None or end_time is None:
            return None, None

        return start_time, end_time

    def __str__(self):
        return self.name
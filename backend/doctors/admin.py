from django.contrib import admin
from .models import Doctor


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "specialization",
        "qualification",
        "experience",
        "consultation_fee",
        "is_available",
    )

    list_filter = (
        "specialization",
        "is_available",
    )

    search_fields = (
        "name",
        "specialization",
        "qualification",
    )

    list_editable = (
        "consultation_fee",
        "is_available",
    )
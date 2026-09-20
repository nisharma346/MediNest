from django.contrib import admin
from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "patient_name",
        "doctor",
        "appointment_date",
        "appointment_time",
        "consultation_fee",
        "payment_status",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "payment_status",
        "appointment_date",
        "doctor",
    )

    search_fields = (
        "patient_name",
        "email",
        "phone",
        "doctor__name",
        "razorpay_order_id",
        "razorpay_payment_id",
    )

    list_editable = (
        "status",
        "payment_status",
    )

    readonly_fields = (
        "razorpay_order_id",
        "razorpay_payment_id",
        "razorpay_signature",
        "paid_at",
        "created_at",
        "updated_at",
    )

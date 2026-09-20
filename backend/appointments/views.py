import hashlib
import hmac
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from doctors.models import Doctor
from .models import Appointment
from .forms import AppointmentForm

try:
    import razorpay
except ImportError:
    razorpay = None


def _verify_razorpay_signature(razorpay_order_id, payment_id, signature):
    if not settings.RAZORPAY_KEY_SECRET:
        return False

    payload = f"{razorpay_order_id}|{payment_id}".encode()
    expected = hmac.new(
        settings.RAZORPAY_KEY_SECRET.encode(),
        payload,
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(expected, signature)


@login_required
def book_appointment(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)

    if not doctor.is_available:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse(
                {"success": False, "message": f"Dr. {doctor.name} is currently unavailable for bookings."},
                status=400,
            )
        messages.error(
            request,
            f"Dr. {doctor.name} is currently unavailable for bookings."
        )
        return redirect("doctors:doctor_detail", pk=doctor.id)

    if request.method == "POST":
        form = AppointmentForm(request.POST, doctor=doctor)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.user = request.user
            appointment.doctor = doctor
            # Fee is strictly populated from Doctor database model
            appointment.consultation_fee = doctor.consultation_fee
            appointment.status = "Pending"
            appointment.payment_status = "pending"
            appointment.save()

            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                if razorpay is None:
                    return JsonResponse(
                        {"success": False, "message": "Razorpay package is not installed on server."},
                        status=400,
                    )

                if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
                    return JsonResponse(
                        {"success": False, "message": "Razorpay payment keys are not configured."},
                        status=400,
                    )

                client = razorpay.Client(
                    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
                )

                amount_in_paise = int(doctor.consultation_fee * 100)

                try:
                    razorpay_order = client.order.create(
                        data={
                            "amount": amount_in_paise,
                            "currency": "INR",
                            "receipt": f"appt_{appointment.id}",
                            "notes": {
                                "appointment_id": str(appointment.id),
                                "doctor_name": doctor.name,
                                "patient_name": appointment.patient_name,
                            },
                        }
                    )
                except Exception as exc:
                    return JsonResponse(
                        {"success": False, "message": f"Razorpay payment setup failed: {exc}"},
                        status=400,
                    )

                appointment.razorpay_order_id = razorpay_order.get("id")
                appointment.save(update_fields=["razorpay_order_id"])

                return JsonResponse(
                    {
                        "success": True,
                        "appointment_id": appointment.id,
                        "razorpay_order_id": appointment.razorpay_order_id,
                        "amount": amount_in_paise,
                        "currency": "INR",
                        "key": settings.RAZORPAY_KEY_ID,
                        "doctor_name": doctor.name,
                        "patient_name": appointment.patient_name,
                        "patient_email": appointment.email,
                        "patient_phone": appointment.phone,
                    }
                )

            # Fallback if non-AJAX
            messages.success(request, f"Appointment #{appointment.id} created. Please complete payment.")
            return redirect("appointments:appointment_detail", appointment_id=appointment.id)
        else:
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                # Extract first error message
                error_msgs = []
                for field, errors in form.errors.items():
                    for err in errors:
                        error_msgs.append(f"{field.replace('_', ' ').title()}: {err}" if field != '__all__' else err)
                return JsonResponse(
                    {"success": False, "message": " | ".join(error_msgs)},
                    status=400,
                )
    else:
        initial_data = {
            "patient_name": request.user.get_full_name() or request.user.username,
            "email": request.user.email,
        }
        form = AppointmentForm(doctor=doctor, initial=initial_data)

    context = {
        "doctor": doctor,
        "form": form,
        "key_id": settings.RAZORPAY_KEY_ID,
    }
    return render(request, "appointments/book_appointment.html", context)


@login_required
@require_POST
def payment_callback(request):
    appointment_id = request.POST.get("appointment_id")
    payment_id = request.POST.get("payment_id")
    razorpay_order_id = request.POST.get("razorpay_order_id")
    signature = request.POST.get("signature")

    if not appointment_id or not payment_id or not razorpay_order_id or not signature:
        return JsonResponse(
            {"success": False, "message": "Incomplete payment callback data."},
            status=400,
        )

    appointment = get_object_or_404(Appointment, id=appointment_id, user=request.user)

    # Security check: razorpay_order_id must match the saved order ID
    if appointment.razorpay_order_id and appointment.razorpay_order_id != razorpay_order_id:
        return JsonResponse(
            {"success": False, "message": "Razorpay order ID mismatch."},
            status=400,
        )

    # Server-side Razorpay signature verification
    if not _verify_razorpay_signature(razorpay_order_id, payment_id, signature):
        appointment.payment_status = "failed"
        appointment.save(update_fields=["payment_status"])
        return JsonResponse(
            {"success": False, "message": "Razorpay payment verification failed."},
            status=400,
        )

    # Successful verification
    appointment.payment_status = "paid"
    appointment.status = "Confirmed"
    appointment.razorpay_payment_id = payment_id
    appointment.razorpay_signature = signature
    appointment.paid_at = timezone.now()
    appointment.save(
        update_fields=[
            "payment_status",
            "status",
            "razorpay_payment_id",
            "razorpay_signature",
            "paid_at",
        ]
    )

    return JsonResponse(
        {
            "success": True,
            "redirect_url": reverse("appointments:appointment_success", args=[appointment.id]),
        }
    )


@login_required
def retry_payment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, user=request.user)

    if appointment.payment_status == "paid":
        return JsonResponse(
            {"success": False, "message": "This appointment has already been paid."},
            status=400,
        )

    if razorpay is None or not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
        return JsonResponse(
            {"success": False, "message": "Razorpay payment system unavailable."},
            status=400,
        )

    client = razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )

    amount_in_paise = int(appointment.consultation_fee * 100)

    try:
        razorpay_order = client.order.create(
            data={
                "amount": amount_in_paise,
                "currency": "INR",
                "receipt": f"appt_{appointment.id}",
                "notes": {
                    "appointment_id": str(appointment.id),
                    "doctor_name": appointment.doctor.name,
                    "patient_name": appointment.patient_name,
                },
            }
        )
    except Exception as exc:
        return JsonResponse(
            {"success": False, "message": f"Payment initialization failed: {exc}"},
            status=400,
        )

    appointment.razorpay_order_id = razorpay_order.get("id")
    appointment.save(update_fields=["razorpay_order_id"])

    return JsonResponse(
        {
            "success": True,
            "appointment_id": appointment.id,
            "razorpay_order_id": appointment.razorpay_order_id,
            "amount": amount_in_paise,
            "currency": "INR",
            "key": settings.RAZORPAY_KEY_ID,
            "doctor_name": appointment.doctor.name,
            "patient_name": appointment.patient_name,
            "patient_email": appointment.email,
            "patient_phone": appointment.phone,
        }
    )


@login_required
def appointment_success(request, appointment_id):
    appointment = get_object_or_404(
        Appointment,
        id=appointment_id,
        user=request.user
    )
    return render(
        request,
        "appointments/appointment_success.html",
        {"appointment": appointment}
    )


@login_required
def my_appointments(request):
    appointments = Appointment.objects.filter(
        user=request.user
    ).select_related("doctor").order_by("-created_at")

    return render(
        request,
        "appointments/my_appointments.html",
        {"appointments": appointments}
    )


@login_required
def appointment_detail(request, appointment_id):
    appointment = get_object_or_404(
        Appointment,
        id=appointment_id,
        user=request.user
    )
    can_cancel = appointment.status in ["Pending", "Confirmed"]

    context = {
        "appointment": appointment,
        "can_cancel": can_cancel,
    }
    return render(request, "appointments/appointment_detail.html", context)


@login_required
def cancel_appointment(request, appointment_id):
    appointment = get_object_or_404(
        Appointment,
        id=appointment_id,
        user=request.user
    )

    if request.method == "POST":
        if appointment.status in ["Pending", "Confirmed"]:
            appointment.status = "Cancelled"
            appointment.save()
            messages.success(
                request,
                f"Appointment #{appointment.id} has been cancelled successfully."
            )
        else:
            messages.error(
                request,
                "This appointment cannot be cancelled."
            )

    return redirect("appointments:appointment_detail", appointment_id=appointment.id)

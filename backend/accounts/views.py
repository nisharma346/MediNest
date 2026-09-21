from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils import timezone

from appointments.models import Appointment
from orders.models import Order
from .forms import ProfileEditForm


def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            return render(
                request,
                "accounts/register.html",
                {"error": "Passwords do not match."}
            )

        from django.contrib.auth.models import User

        if User.objects.filter(username=username).exists():
            return render(
                request,
                "accounts/register.html",
                {"error": "Username already exists."}
            )

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        login(request, user)

        return redirect("core:home")

    return render(request, "accounts/register.html")


def user_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect("core:home")

        return render(
            request,
            "accounts/login.html",
            {"error": "Invalid username or password."}
        )

    return render(request, "accounts/login.html")


@login_required
def user_logout(request):
    logout(request)
    return redirect("core:home")


@login_required(login_url="accounts:login")
def dashboard(request):
    user = request.user
    today = timezone.now().date()

    user_orders = Order.objects.filter(user=user)
    user_appointments = Appointment.objects.filter(user=user).select_related("doctor")

    total_orders = user_orders.count()
    active_orders = user_orders.exclude(status__in=["delivered", "cancelled"]).count()
    upcoming_appointments = user_appointments.filter(
        appointment_date__gte=today
    ).exclude(status__in=["Cancelled", "Completed"]).count()
    completed_appointments = user_appointments.filter(status="Completed").count()

    recent_orders = user_orders.order_by("-created_at")[:3]
    appointments = user_appointments.filter(
        appointment_date__gte=today
    ).exclude(status__in=["Cancelled", "Completed"]).order_by(
        "appointment_date", "appointment_time"
    )[:3]

    latest_order = user_orders.order_by("-created_at").first()
    user_name = user.get_full_name() or user.first_name or user.username

    profile_phone = latest_order.phone if latest_order else "Not available"
    profile_address = "Not available"
    if latest_order:
        address_parts = [
            latest_order.address_line1,
            latest_order.address_line2,
            latest_order.city,
            latest_order.state,
            latest_order.pincode,
        ]
        profile_address = ", ".join(part for part in address_parts if part)

    context = {
        "user_name": user_name,
        "total_orders": total_orders,
        "active_orders": active_orders,
        "upcoming_appointments": upcoming_appointments,
        "completed_appointments": completed_appointments,
        "total_appointments": user_appointments.count(),
        "recent_orders": recent_orders,
        "upcoming_appointment_list": appointments,
        "profile_phone": profile_phone,
        "profile_address": profile_address,
        "email": user.email,
    }
    return render(request, "accounts/dashboard.html", context)


@login_required(login_url="accounts:login")
def edit_profile(request):
    user = request.user
    latest_order = Order.objects.filter(user=user).order_by("-created_at").first()

    initial_data = {
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "phone_number": latest_order.phone if latest_order else "",
        "address": latest_order.address_line1 if latest_order else "",
        "city": latest_order.city if latest_order else "",
        "state": latest_order.state if latest_order else "",
        "pincode": latest_order.pincode if latest_order else "",
        "user_pk": user.pk,
    }

    if request.method == "POST":
        form = ProfileEditForm(request.POST, initial=initial_data)
        form.initial = initial_data
        if form.is_valid():
            user.first_name = form.cleaned_data["first_name"] or ""
            user.last_name = form.cleaned_data["last_name"] or ""
            user.email = form.cleaned_data["email"]
            user.save(update_fields=["first_name", "last_name", "email"])

            if latest_order:
                latest_order.phone = form.cleaned_data["phone_number"] or ""
                latest_order.address_line1 = form.cleaned_data["address"] or ""
                latest_order.city = form.cleaned_data["city"] or ""
                latest_order.state = form.cleaned_data["state"] or ""
                latest_order.pincode = form.cleaned_data["pincode"] or ""
                latest_order.save(update_fields=["phone", "address_line1", "city", "state", "pincode"])

            messages.success(request, "Your profile has been updated successfully.")
            return redirect("accounts:dashboard")
    else:
        form = ProfileEditForm(initial=initial_data)

    return render(request, "accounts/edit_profile.html", {"form": form})
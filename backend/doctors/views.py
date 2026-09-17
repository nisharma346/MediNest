from django.shortcuts import render
from .models import Doctor


def doctor_list(request):
    doctors = Doctor.objects.filter(
        is_available=True
    ).order_by("name")

    return render(
        request,
        "doctors/doctor_list.html",
        {"doctors": doctors}
    )
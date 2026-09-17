from django.urls import path
from .views import doctor_list

app_name = "doctors"

urlpatterns = [
    path("", doctor_list, name="doctor_list"),
]
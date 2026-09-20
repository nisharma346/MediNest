from django.urls import path
from . import views

app_name = "appointments"

urlpatterns = [
    path("book/<int:doctor_id>/", views.book_appointment, name="book_appointment"),
    path("payment-callback/", views.payment_callback, name="payment_callback"),
    path("retry-payment/<int:appointment_id>/", views.retry_payment, name="retry_payment"),
    path("success/<int:appointment_id>/", views.appointment_success, name="appointment_success"),
    path("my-appointments/", views.my_appointments, name="my_appointments"),
    path("<int:appointment_id>/", views.appointment_detail, name="appointment_detail"),
    path("<int:appointment_id>/cancel/", views.cancel_appointment, name="cancel_appointment"),
]

from datetime import date, time

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from appointments.models import Appointment
from doctors.models import Doctor
from orders.models import Order


class DashboardAccessTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="alice",
            email="alice@example.com",
            password="secret123",
            first_name="Alice",
            last_name="Smith",
        )
        self.other_user = get_user_model().objects.create_user(
            username="bob",
            email="bob@example.com",
            password="secret123",
            first_name="Bob",
            last_name="Jones",
        )

        self.doctor = Doctor.objects.create(
            name="Ananya Sharma",
            specialization="Cardiologist",
            qualification="MBBS, MD",
            experience=10,
            consultation_fee=199.86,
            available_days="Monday, Wednesday, Friday",
            available_time="10:00 AM - 2:00 PM",
        )

        self.order = Order.objects.create(
            user=self.user,
            full_name="Alice Smith",
            phone="9876543210",
            address_line1="12 Health Lane",
            address_line2="",
            city="Delhi",
            state="Delhi",
            pincode="110001",
            payment_method="razorpay",
            status="confirmed",
            total_amount=299.00,
        )

        self.other_order = Order.objects.create(
            user=self.other_user,
            full_name="Bob Jones",
            phone="9123456789",
            address_line1="99 Other St",
            city="Bengaluru",
            state="Karnataka",
            pincode="560001",
            payment_method="cod",
            status="pending",
            total_amount=150.00,
        )

        self.appointment = Appointment.objects.create(
            user=self.user,
            doctor=self.doctor,
            appointment_date=date(2030, 1, 15),
            appointment_time=time(10, 30),
            patient_name="Alice Smith",
            phone="9876543210",
            email="alice@example.com",
            symptoms="Chest pain",
            consultation_fee=199.86,
            status="Confirmed",
            payment_status="paid",
        )

        self.other_appointment = Appointment.objects.create(
            user=self.other_user,
            doctor=self.doctor,
            appointment_date=date(2030, 2, 15),
            appointment_time=time(11, 0),
            patient_name="Bob Jones",
            phone="9123456789",
            email="bob@example.com",
            symptoms="Fever",
            consultation_fee=199.86,
            status="Pending",
            payment_status="pending",
        )

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("accounts:dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("accounts/login", response.url)

    def test_dashboard_only_shows_current_user_data(self):
        self.client.login(username="alice", password="secret123")
        response = self.client.get(reverse("accounts:dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Welcome back, Alice")
        self.assertEqual(response.context["total_orders"], 1)
        self.assertEqual(response.context["total_appointments"], 1)
        self.assertEqual(response.context["upcoming_appointments"], 1)
        self.assertNotIn(self.other_order.id, [item.id for item in response.context["recent_orders"]])
        self.assertNotIn(self.other_appointment.id, [item.id for item in response.context["upcoming_appointment_list"]])

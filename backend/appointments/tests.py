from datetime import date

from django.test import TestCase

from appointments.forms import AppointmentForm
from doctors.models import Doctor


class AppointmentAvailabilityValidationTests(TestCase):
    def setUp(self):
        self.doctor = Doctor.objects.create(
            name="Ananya Sharma",
            specialization="Cardiologist",
            qualification="MBBS, MD",
            experience=10,
            consultation_fee=199.86,
            available_days="Monday, Wednesday, Friday",
            available_time="10:00 AM - 2:00 PM",
        )

    def test_rejects_day_outside_doctor_schedule(self):
        form = AppointmentForm(
            data={
                "appointment_date": "2030-01-17",  # Thursday
                "appointment_time": "11:00",
                "patient_name": "Alice Smith",
                "phone": "9876543210",
                "email": "alice@example.com",
                "symptoms": "Chest pain",
            },
            doctor=self.doctor,
        )

        self.assertFalse(form.is_valid())
        self.assertIn("only available on Monday, Wednesday, Friday", form.errors["appointment_date"][0])

    def test_rejects_time_outside_consultation_hours(self):
        form = AppointmentForm(
            data={
                "appointment_date": "2030-01-14",  # Monday
                "appointment_time": "09:00",
                "patient_name": "Alice Smith",
                "phone": "9876543210",
                "email": "alice@example.com",
                "symptoms": "Chest pain",
            },
            doctor=self.doctor,
        )

        self.assertFalse(form.is_valid())
        self.assertIn("between 10:00 AM and 2:00 PM", form.errors["appointment_time"][0])

    def test_accepts_time_within_consultation_hours(self):
        form = AppointmentForm(
            data={
                "appointment_date": "2030-01-14",  # Monday
                "appointment_time": "11:30",
                "patient_name": "Alice Smith",
                "phone": "9876543210",
                "email": "alice@example.com",
                "symptoms": "Chest pain",
            },
            doctor=self.doctor,
        )

        self.assertTrue(form.is_valid(), form.errors)

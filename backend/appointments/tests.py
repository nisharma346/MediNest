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


from io import StringIO
from django.core.management import call_command
from appointments.utils import get_razorpay_diagnostic, verify_razorpay_auth


class RazorpayDiagnosticTests(TestCase):
    def test_diagnostic_helper(self):
        diag = get_razorpay_diagnostic()
        self.assertIn("key_id_exists", diag)
        self.assertIn("key_secret_exists", diag)
        self.assertIn("is_test_mode", diag)
        self.assertIn("sdk_installed", diag)
        self.assertTrue(diag["sdk_installed"])

    def test_check_razorpay_management_command(self):
        out = StringIO()
        call_command("check_razorpay", stdout=out)
        output = out.getvalue()
        self.assertIn("Razorpay Configuration Diagnostic", output)
        self.assertIn("Razorpay Authentication Check", output)
        # Ensure secret key is NEVER printed in command output
        from django.conf import settings
        if settings.RAZORPAY_KEY_SECRET:
            self.assertNotIn(settings.RAZORPAY_KEY_SECRET, output)

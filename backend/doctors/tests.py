from django.test import TestCase
from django.urls import reverse

from .models import Doctor


class DoctorPublicVisibilityTests(TestCase):
    def setUp(self):
        self.available_doctor = Doctor.objects.create(
            name="Dr. Available Doctor",
            specialization="General Physician",
            qualification="MBBS, MD",
            experience=10,
            consultation_fee=500.00,
            available_days="Monday, Wednesday",
            available_time="10:00 AM - 2:00 PM",
            is_available=True,
        )
        self.unavailable_doctor = Doctor.objects.create(
            name="Dr. Hidden Doctor",
            specialization="Dermatologist",
            qualification="MBBS, MD",
            experience=8,
            consultation_fee=700.00,
            available_days="Tuesday",
            available_time="1:00 PM - 3:00 PM",
            is_available=False,
        )

    def test_public_doctor_list_and_detail_only_show_available_doctors(self):
        list_response = self.client.get(reverse("doctors:doctor_list"))
        self.assertContains(list_response, self.available_doctor.name)
        self.assertNotContains(list_response, self.unavailable_doctor.name)

        detail_response = self.client.get(reverse("doctors:doctor_detail", args=[self.available_doctor.pk]))
        self.assertEqual(detail_response.status_code, 200)

        hidden_response = self.client.get(reverse("doctors:doctor_detail", args=[self.unavailable_doctor.pk]))
        self.assertEqual(hidden_response.status_code, 404)


class DoctorDisplayNameTests(TestCase):
    def test_display_name_adds_single_doctor_prefix(self):
        doctor = Doctor(
            name="Ananya Sharma",
            specialization="Cardiologist",
            qualification="MBS, MD",
            experience=10,
            consultation_fee=199.86,
            available_days="Monday, Wednesday, Friday",
            available_time="10:00 AM - 2:00 PM",
        )

        self.assertEqual(doctor.display_name, "Dr. Ananya Sharma")
        self.assertEqual(doctor.name, "Ananya Sharma")

    def test_display_name_removes_duplicate_prefixes_without_changing_db(self):
        doctor = Doctor(
            name="Dr. Dr. Ananya Sharma",
            specialization="Cardiologist",
            qualification="MBS, MD",
            experience=10,
            consultation_fee=199.86,
            available_days="Monday, Wednesday, Friday",
            available_time="10:00 AM - 2:00 PM",
        )

        self.assertEqual(doctor.display_name, "Dr. Ananya Sharma")
        self.assertEqual(doctor.name, "Dr. Dr. Ananya Sharma")

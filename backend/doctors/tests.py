from django.test import TestCase

from .models import Doctor


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

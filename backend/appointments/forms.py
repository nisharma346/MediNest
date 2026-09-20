from django import forms
from django.utils import timezone
from .models import Appointment


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = [
            'appointment_date',
            'appointment_time',
            'patient_name',
            'phone',
            'email',
            'symptoms',
        ]
        widgets = {
            'appointment_date': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control',
                    'min': timezone.now().date().isoformat()
                }
            ),
            'appointment_time': forms.TimeInput(
                attrs={
                    'type': 'time',
                    'class': 'form-control'
                }
            ),
            'patient_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Full Name'
                }
            ),
            'phone': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Phone Number'
                }
            ),
            'email': forms.EmailInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Email Address'
                }
            ),
            'symptoms': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'Describe your symptoms or reason for consultation'
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        self.doctor = kwargs.pop('doctor', None)
        super().__init__(*args, **kwargs)

    def clean_appointment_date(self):
        appointment_date = self.cleaned_data.get('appointment_date')
        if not appointment_date:
            raise forms.ValidationError("Please select a valid appointment date.")

        if appointment_date < timezone.now().date():
            raise forms.ValidationError("Appointment date cannot be in the past.")

        if self.doctor and self.doctor.available_days:
            weekday = appointment_date.strftime("%A")
            # Parse available days (e.g., "Monday, Wednesday, Friday")
            available_days_list = [
                d.strip().lower() for d in self.doctor.available_days.split(",")
            ]
            if weekday.lower() not in available_days_list:
                raise forms.ValidationError(
                    f"Dr. {self.doctor.name} is only available on {self.doctor.available_days}."
                )

        return appointment_date

    def clean_appointment_time(self):
        appointment_time = self.cleaned_data.get('appointment_time')
        if not appointment_time:
            raise forms.ValidationError("Please select a valid appointment time.")
        return appointment_time

    def clean(self):
        cleaned_data = super().clean()
        appointment_date = cleaned_data.get('appointment_date')
        appointment_time = cleaned_data.get('appointment_time')

        if appointment_date and appointment_time and self.doctor:
            # Prevent double booking: check if an active appointment already exists for this doctor, date, and time
            existing_query = Appointment.objects.filter(
                doctor=self.doctor,
                appointment_date=appointment_date,
                appointment_time=appointment_time
            ).exclude(status='Cancelled')

            if self.instance and self.instance.pk:
                existing_query = existing_query.exclude(pk=self.instance.pk)

            if existing_query.exists():
                raise forms.ValidationError(
                    f"Dr. {self.doctor.name} is already booked for the selected date ({appointment_date}) and time slot ({appointment_time.strftime('%I:%M %p')}). Please choose a different slot."
                )

        return cleaned_data

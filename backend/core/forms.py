import re
from django import forms
from .models import ContactMessage


class ContactForm(forms.ModelForm):
    name = forms.CharField(
        required=True,
        error_messages={
            "required": "Full name is required.",
        },
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Your Full Name",
            }
        )
    )

    email = forms.EmailField(
        required=True,
        error_messages={
            "required": "Email address is required.",
            "invalid": "Enter a valid email address.",
        },
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "name@example.com",
            }
        )
    )

    phone = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Phone Number (Optional)",
            }
        )
    )

    subject = forms.CharField(
        required=True,
        error_messages={
            "required": "Subject is required.",
        },
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Subject of your message",
            }
        )
    )

    message = forms.CharField(
        required=True,
        error_messages={
            "required": "Message content is required.",
        },
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 5,
                "placeholder": "Write your detailed message here...",
            }
        )
    )

    class Meta:
        model = ContactMessage
        fields = ["name", "email", "phone", "subject", "message"]

    def clean_name(self):
        name = self.cleaned_data.get("name", "").strip()
        if not name:
            raise forms.ValidationError("Full name is required.")
        return name

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip()
        if not email:
            raise forms.ValidationError("Email address is required.")
        return email

    def clean_subject(self):
        subject = self.cleaned_data.get("subject", "").strip()
        if not subject:
            raise forms.ValidationError("Subject is required.")
        return subject

    def clean_message(self):
        message = self.cleaned_data.get("message", "").strip()
        if not message:
            raise forms.ValidationError("Message content is required.")
        return message

    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "").strip()
        if phone:
            # Validate optional phone number format (allow +, digits, spaces, dashes, parentheses)
            if not re.match(r"^[+\d\s\-\(\)]{7,20}$", phone):
                raise forms.ValidationError("Please enter a valid phone number (e.g. +1 234 567 8900).")
        return phone

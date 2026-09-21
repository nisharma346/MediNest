from django import forms
from django.contrib.auth import get_user_model


class ProfileEditForm(forms.Form):
    first_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter your first name",
        })
    )
    last_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter your last name",
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "Enter your email address",
        })
    )
    phone_number = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter your phone number",
        })
    )
    address = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter your address",
        })
    )
    city = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter city",
        })
    )
    state = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter state",
        })
    )
    pincode = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter pincode",
        })
    )

    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").strip()
        if not email:
            raise forms.ValidationError("Email is required.")

        user_model = get_user_model()
        existing_user = user_model.objects.filter(email__iexact=email).exclude(pk=self.initial.get("user_pk")).first()
        if existing_user:
            raise forms.ValidationError("This email address is already in use.")

        return email

from django.core.management.base import BaseCommand
from appointments.utils import get_razorpay_diagnostic, verify_razorpay_auth


class Command(BaseCommand):
    help = "Safely checks Razorpay configuration and verifies authentication without exposing secrets."

    def handle(self, *args, **options):
        self.stdout.write("--- Razorpay Configuration Diagnostic ---")
        diag = get_razorpay_diagnostic()

        self.stdout.write(f"RAZORPAY_KEY_ID exists: {'Yes' if diag['key_id_exists'] else 'No'}")
        self.stdout.write(f"RAZORPAY_KEY_SECRET exists: {'Yes' if diag['key_secret_exists'] else 'No'}")
        self.stdout.write(f"Key ID Prefix Mode: {diag['mode_str']}")
        self.stdout.write(f"Both values non-empty: {'Yes' if diag['is_non_empty'] else 'No'}")
        self.stdout.write(f"Razorpay Python SDK installed: {'Yes' if diag['sdk_installed'] else 'No'}")

        self.stdout.write("\n--- Razorpay Authentication Check ---")
        success, message = verify_razorpay_auth()

        if success:
            self.stdout.write(self.style.SUCCESS(message))
        else:
            self.stdout.write(self.style.ERROR(message))

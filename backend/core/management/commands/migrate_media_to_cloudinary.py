import os

from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand

try:
    import cloudinary
    import cloudinary.uploader
    HAS_CLOUDINARY = True
except ImportError:
    HAS_CLOUDINARY = False


class Command(BaseCommand):
    help = "Uploads existing local media files to Cloudinary and updates database references."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Simulate the migration without uploading files or modifying database records.",
        )

    def handle(self, *args, **options):
        dry_run = options.get("dry_run", False)

        if dry_run:
            self.stdout.write(self.style.WARNING("=== RUNNING IN DRY-RUN MODE ==="))

        cloudinary_url = getattr(settings, "CLOUDINARY_URL", None) or os.environ.get("CLOUDINARY_URL")

        if not HAS_CLOUDINARY:
            self.stderr.write(self.style.ERROR("The 'cloudinary' package is not installed."))
            return

        if not cloudinary_url and not dry_run:
            self.stdout.write(
                self.style.WARNING(
                    "CLOUDINARY_URL environment variable is not configured. "
                    "Running inspection mode on local media files."
                )
            )

        # Target models and fields containing media files
        TARGET_MODELS = [
            ("doctors", "Doctor", ["profile_image"]),
            ("core", "Service", ["image"]),
            ("core", "Testimonial", ["profile_image"]),
            ("core", "HealthUpdate", ["image"]),
            ("core", "GalleryItem", ["image"]),
            ("products", "Category", ["image"]),
            ("products", "Product", ["image"]),
            ("blog", "Article", ["featured_image"]),
        ]

        total_uploaded = 0
        total_already_cloudinary = 0
        total_missing = 0
        total_failed = 0
        total_empty = 0

        for app_label, model_name, field_names in TARGET_MODELS:
            try:
                model = apps.get_model(app_label, model_name)
            except LookupError:
                self.stdout.write(self.style.ERROR(f"Model {app_label}.{model_name} not found."))
                continue

            self.stdout.write(self.style.MIGRATE_HEADING(f"\nChecking model: {app_label}.{model_name}"))

            for instance in model.objects.all():
                for field_name in field_names:
                    file_field = getattr(instance, field_name, None)
                    if not file_field or not str(file_field).strip():
                        total_empty += 1
                        continue

                    raw_val = str(file_field).strip()

                    # Check if already a Cloudinary URL or remote URL
                    if (
                        raw_val.startswith("http://")
                        or raw_val.startswith("https://")
                        or "res.cloudinary.com" in raw_val
                        or "cloudinary.com" in raw_val
                    ):
                        self.stdout.write(
                            f"  [{model_name} #{instance.pk}] '{field_name}': Already Cloudinary URL ({raw_val})"
                        )
                        total_already_cloudinary += 1
                        continue

                    # Check for local file existence
                    relative_path = raw_val
                    if relative_path.startswith("media/"):
                        relative_path = relative_path[6:]

                    local_filepath = settings.MEDIA_ROOT / relative_path

                    if not local_filepath.exists():
                        alt_filepath = settings.MEDIA_ROOT / raw_val
                        if alt_filepath.exists():
                            local_filepath = alt_filepath
                        else:
                            self.stdout.write(
                                self.style.WARNING(
                                    f"  [{model_name} #{instance.pk}] '{field_name}': Missing local file ({raw_val})"
                                )
                            )
                            total_missing += 1
                            continue

                    self.stdout.write(
                        f"  [{model_name} #{instance.pk}] '{field_name}': Local file found at {local_filepath}"
                    )

                    if dry_run or not cloudinary_url:
                        self.stdout.write("    [INSPECTION/DRY-RUN] Would upload to Cloudinary and update database record.")
                        total_uploaded += 1
                        continue

                    # Perform upload to Cloudinary
                    try:
                        field_obj = model._meta.get_field(field_name)
                        upload_to = getattr(field_obj, "upload_to", "") or model_name.lower()
                        folder = str(upload_to).rstrip("/")

                        base_name = os.path.splitext(os.path.basename(str(local_filepath)))[0]

                        result = cloudinary.uploader.upload(
                            str(local_filepath),
                            folder=folder,
                            public_id=base_name,
                            use_filename=True,
                            unique_filename=False,
                            overwrite=True,
                            resource_type="auto",
                        )

                        secure_url = result.get("secure_url") or result.get("url")

                        setattr(instance, field_name, secure_url)
                        instance.save(update_fields=[field_name])

                        self.stdout.write(
                            self.style.SUCCESS(
                                f"    Successfully uploaded -> {secure_url}"
                            )
                        )
                        total_uploaded += 1
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(
                                f"    Failed to upload {local_filepath}: {str(e)}"
                            )
                        )
                        total_failed += 1

        self.stdout.write(self.style.MIGRATE_HEADING("\n" + "=" * 40))
        self.stdout.write(self.style.MIGRATE_HEADING("MIGRATION SUMMARY"))
        self.stdout.write(self.style.MIGRATE_HEADING("=" * 40))
        self.stdout.write(self.style.SUCCESS(f"Uploaded: {total_uploaded}"))
        self.stdout.write(self.style.SUCCESS(f"Already Cloudinary: {total_already_cloudinary}"))
        self.stdout.write(self.style.WARNING(f"Missing local file: {total_missing}"))
        self.stdout.write(self.style.ERROR(f"Failed: {total_failed}"))

import os
from pathlib import Path

from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import models

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
            "--upload",
            action="store_true",
            help="Execute actual upload of local media files to Cloudinary and update database records.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Simulate the migration without uploading files or modifying database records.",
        )

    def _normalize_local_path_candidates(self, raw_value, media_root):
        value = str(raw_value or "").strip()
        if not value:
            return []

        candidates = []
        normalized = value.replace("\\", "/")
        if normalized.startswith("http://") or normalized.startswith("https://"):
            return []

        if "/backend/media/" in normalized:
            normalized = normalized.split("/backend/media/", 1)[1]
        elif normalized.startswith("/media/") or normalized.startswith("media/"):
            normalized = normalized.split("/media/", 1)[1] if "/media/" in normalized else normalized.split("media/", 1)[1]
        elif "media/" in normalized:
            normalized = normalized.split("media/", 1)[1]

        normalized = normalized.lstrip("/")

        if normalized:
            candidates.append((media_root / normalized).resolve())
            candidates.append((media_root.parent / normalized).resolve())

        absolute_candidate = Path(value)
        if absolute_candidate.is_absolute():
            candidates.append(absolute_candidate.resolve())

        deduped = []
        seen = set()
        for candidate in candidates:
            key = str(candidate)
            if key not in seen:
                seen.add(key)
                deduped.append(candidate)
        return deduped

    def _build_cloudinary_folder(self, app_label, model_name, field_obj, instance):
        upload_to = getattr(field_obj, "upload_to", "") or ""
        if callable(upload_to):
            try:
                upload_to = upload_to(instance, os.path.basename(str(getattr(instance, field_obj.name))))
            except TypeError:
                upload_to = ""

        upload_to_value = str(upload_to).strip("/").replace("\\", "/")
        if upload_to_value:
            return "/".join(part for part in [app_label, model_name.lower(), upload_to_value] if part and part not in (".", "/"))
        return "/".join(part for part in [app_label, model_name.lower()] if part)

    def _find_media_fields(self):
        model_specs = []
        seen = set()
        for model in apps.get_models():
            media_fields = []
            for field in model._meta.get_fields():
                if isinstance(field, (models.ImageField, models.FileField)):
                    key = (model._meta.app_label, model._meta.object_name, field.name)
                    if key not in seen:
                        seen.add(key)
                        media_fields.append(field)
            if media_fields:
                model_specs.append((model, media_fields))
        return model_specs

    def handle(self, *args, **options):
        dry_run = options.get("dry_run", False)
        upload_mode = options.get("upload", False) and not dry_run

        cloudinary_url = getattr(settings, "CLOUDINARY_URL", None) or os.environ.get("CLOUDINARY_URL")

        if upload_mode:
            if not HAS_CLOUDINARY:
                self.stderr.write(self.style.ERROR("ERROR: The 'cloudinary' package is not installed."))
                return

            if not cloudinary_url:
                self.stderr.write(
                    self.style.ERROR(
                        "ERROR: The --upload flag requires CLOUDINARY_URL to be configured in the environment.\n"
                        "CLOUDINARY_URL is missing. Aborting migration without making any changes."
                    )
                )
                return
            self.stdout.write(self.style.SUCCESS("=== RUNNING IN PRODUCTION UPLOAD MODE ==="))
        else:
            self.stdout.write(self.style.WARNING("=== RUNNING IN INSPECTION / DRY-RUN MODE ==="))
            self.stdout.write(self.style.WARNING("Pass --upload with CLOUDINARY_URL configured to execute actual uploads.\n"))

        media_root = Path(getattr(settings, "MEDIA_ROOT", "media")).resolve()
        model_specs = self._find_media_fields()

        total_models = len(model_specs)
        total_media_fields = sum(len(fields) for _, fields in model_specs)
        local_files_detected = 0
        total_uploaded = 0
        total_already_cloudinary = 0
        total_missing = 0
        total_failed = 0
        total_empty = 0

        self.stdout.write(self.style.MIGRATE_HEADING(f"Discovered {total_models} models with {total_media_fields} media fields."))
        for model, fields in model_specs:
            field_names = [field.name for field in fields]
            self.stdout.write(f"  - {model._meta.app_label}.{model._meta.object_name}: {', '.join(field_names) or 'none'}")

        for model, fields in model_specs:
            app_label = model._meta.app_label
            model_name = model._meta.object_name
            self.stdout.write(self.style.MIGRATE_HEADING(f"\nChecking model: {app_label}.{model_name}"))

            for instance in model.objects.all():
                for field in fields:
                    field_name = field.name
                    file_field = getattr(instance, field_name, None)
                    if not file_field or not str(file_field).strip():
                        total_empty += 1
                        continue

                    raw_value = str(file_field).strip()
                    if (
                        raw_value.startswith("http://")
                        or raw_value.startswith("https://")
                        or "res.cloudinary.com" in raw_value
                        or "cloudinary.com" in raw_value
                    ):
                        self.stdout.write(
                            f"  [{model_name} #{instance.pk}] '{field_name}': Already Cloudinary URL ({raw_value})"
                        )
                        total_already_cloudinary += 1
                        continue

                    local_candidates = self._normalize_local_path_candidates(raw_value, media_root)
                    local_filepath = None
                    for candidate in local_candidates:
                        if candidate.exists() and candidate.is_file():
                            local_filepath = candidate
                            break

                    if local_filepath is None:
                        self.stdout.write(
                            self.style.WARNING(
                                f"  [{model_name} #{instance.pk}] '{field_name}': Missing local file for value '{raw_value}'"
                            )
                        )
                        total_missing += 1
                        continue

                    local_files_detected += 1
                    folder = self._build_cloudinary_folder(app_label, model_name, field, instance)

                    if not upload_mode:
                        self.stdout.write(
                            f"  [{model_name} #{instance.pk}] '{field_name}': Local file found at {local_filepath}"
                        )
                        self.stdout.write(
                            f"    [DRY-RUN] Would upload '{local_filepath}' to Cloudinary folder '{folder}' and update DB record."
                        )
                        total_uploaded += 1
                        continue

                    self.stdout.write(
                        f"  [{model_name} #{instance.pk}] Uploading local file '{local_filepath}' to Cloudinary folder '{folder}'..."
                    )

                    try:
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
                            self.style.SUCCESS(f"    Successfully uploaded -> {secure_url}")
                        )
                        total_uploaded += 1
                    except Exception as exc:
                        self.stdout.write(
                            self.style.ERROR(f"    Failed to upload {local_filepath}: {exc}")
                        )
                        total_failed += 1

        self.stdout.write(self.style.MIGRATE_HEADING("\n" + "=" * 56))
        self.stdout.write(self.style.MIGRATE_HEADING("MIGRATION SUMMARY"))
        self.stdout.write(self.style.MIGRATE_HEADING("=" * 56))
        self.stdout.write(self.style.SUCCESS(f"Models discovered: {total_models}"))
        self.stdout.write(self.style.SUCCESS(f"Media fields discovered: {total_media_fields}"))
        self.stdout.write(self.style.SUCCESS(f"Local files detected: {local_files_detected}"))
        self.stdout.write(self.style.SUCCESS(f"Uploaded: {total_uploaded}"))
        self.stdout.write(self.style.SUCCESS(f"Already Cloudinary: {total_already_cloudinary}"))
        self.stdout.write(self.style.WARNING(f"Missing local files: {total_missing}"))
        self.stdout.write(self.style.ERROR(f"Failed uploads: {total_failed}"))
        self.stdout.write(self.style.WARNING(f"Empty values skipped: {total_empty}"))

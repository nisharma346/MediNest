"""
Run this script to upload all local doctor images to Cloudinary.
Usage: cd backend && python upload_to_cloudinary.py
"""

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "medinest.settings")

# Force Cloudinary storage before django setup
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# Temporarily restore CLOUDINARY_URL if commented out in .env
cloudinary_url = os.getenv("CLOUDINARY_URL")
if not cloudinary_url:
    print("❌ CLOUDINARY_URL not found in .env!")
    print("   Please uncomment CLOUDINARY_URL in backend/.env and try again.")
    exit(1)

django.setup()

import cloudinary
import cloudinary.uploader
from doctors.models import Doctor

# Configure cloudinary
cloudinary.config(cloudinary_url=cloudinary_url)

MEDIA_ROOT = BASE_DIR / "media"
doctors_folder = MEDIA_ROOT / "doctors"

print("=" * 60)
print("Uploading Doctor Images to Cloudinary...")
print("=" * 60)

success_count = 0
fail_count = 0

for doctor in Doctor.objects.all():
    name_part = doctor.name.replace(" ", "_").replace(".", "_")
    
    image_file = None
    if doctor.profile_image:
        stored_path = str(doctor.profile_image)
        local_path = MEDIA_ROOT / stored_path
        if local_path.exists():
            image_file = local_path

    if not image_file:
        if doctors_folder.exists():
            for f in doctors_folder.iterdir():
                if name_part.lower() in f.name.lower():
                    image_file = f
                    break

    if not image_file:
        print(f"[SKIP] {doctor.name}: Local image not found")
        fail_count += 1
        continue

    try:
        public_id = f"media/doctors/{image_file.stem}"
        
        result = cloudinary.uploader.upload(
            str(image_file),
            public_id=public_id,
            overwrite=True,
            resource_type="image",
        )
        
        doctor.profile_image = f"doctors/{image_file.name}"
        doctor.save()
        
        print(f"[OK] {doctor.name}")
        print(f"      -> {result['secure_url']}")
        success_count += 1

    except Exception as e:
        print(f"[FAIL] {doctor.name}: {e}")
        fail_count += 1

print("=" * 60)
print(f"Uploaded: {success_count} | Failed: {fail_count}")
print("=" * 60)

if success_count > 0:
    print("Done! Now deploy to Vercel -- images will show correctly.")

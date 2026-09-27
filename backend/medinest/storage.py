from django.core.files.storage import FileSystemStorage


class MediaFileSystemStorage(FileSystemStorage):
    """
    Custom FileSystemStorage for local development that safely returns absolute URLs
    (e.g. http:// or https:// Cloudinary URLs) as-is without prepending MEDIA_URL.
    """
    def url(self, name):
        if name and (name.startswith("http://") or name.startswith("https://")):
            return name
        return super().url(name)

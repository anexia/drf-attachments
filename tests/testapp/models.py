from django.db import models

from drf_attachments.models.fields import AttachmentRelation


class PhotoAlbum(models.Model):
    """
    Photo album with any number of JPEG photos and PDF scans as attachments.
    """

    name = models.CharField(max_length=50, primary_key=True)
    attachments = AttachmentRelation()

    class AttachmentMeta:
        valid_mime_types = ["image/jpeg", "application/pdf"]
        valid_extensions = [".jpg", ".jpeg", ".pdf"]


class Thumbnail(models.Model):
    """
    Thumbnail collection with one JPEG image per context as attachments.
    """

    name = models.CharField(max_length=50, primary_key=True)
    attachments = AttachmentRelation()

    class AttachmentMeta:
        valid_mime_types = ["image/jpeg"]
        valid_extensions = [".jpg"]
        unique_upload_per_context = True


class Diagram(models.Model):
    """
    Single diagram with an SVG file as attachment.
    """

    name = models.CharField(max_length=50, primary_key=True)
    attachments = AttachmentRelation()

    class AttachmentMeta:
        valid_mime_types = ["image/svg+xml"]
        valid_extensions = [".svg"]
        unique_upload = True


class File(models.Model):
    """
    Single file in arbitrary format with constrained file size.
    """

    name = models.CharField(max_length=50, primary_key=True)
    attachments = AttachmentRelation()

    class AttachmentMeta:
        unique_upload = True
        min_size = 1_000  # Bytes
        max_size = 10_000  # Bytes


class Profile(models.Model):
    """
    User profile with one avatar image as attachment.
    """

    name = models.CharField(max_length=50, primary_key=True)
    attachments = AttachmentRelation()

    class AttachmentMeta:
        valid_mime_types = ["image/jpeg"]
        valid_extensions = [".jpg", ".jpeg"]
        unique_upload = True

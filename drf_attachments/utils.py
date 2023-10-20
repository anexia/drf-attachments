import os

import magic
from django.urls import reverse


def get_mime_type(file):
    """
    Get MIME by reading the header of the file
    """
    initial_pos = file.tell()
    file.seek(0)
    mime_type = magic.from_buffer(file.read(1024), mime=True)
    file.seek(initial_pos)
    return mime_type


def get_extension(file):
    filename, file_extension = os.path.splitext(file.name)
    return file_extension.lower()


def remove_file(file_path, raise_exceptions=False):
    if not os.path.isfile(file_path):
        return

    try:
        os.remove(file_path)
    except Exception:
        if raise_exceptions:
            # forward the thrown exception
            raise
        # just continue if deletion of old file was not possible and no exceptions should be raised


def get_api_attachment_url(attachment_pk):
    return reverse("attachment-download", kwargs={"pk": attachment_pk})

def get_admin_attachment_url(attachment_pk):
    return reverse(
        "admin:drf_attachments_attachment_download",
        kwargs={
            "object_id": attachment_pk
        }
    )

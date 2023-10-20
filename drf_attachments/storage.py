import os
from uuid import uuid1

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.utils import timezone

__all__ = [
    "AttachmentFileStorage",
    "attachment_upload_path",
]

from drf_attachments.utils import get_admin_attachment_url


class AttachmentFileStorage(FileSystemStorage):
    """
    This is used to store attachments in a folder that is not mode publicly available by the webserver
    Attachments are served with a dedicated API route instead
    """

    def __init__(self):
        super().__init__(location=settings.PRIVATE_ROOT)

    def url(self, name):
        from drf_attachments.models import Attachment

        attachment = Attachment.objects.filter(file=name).first()
        if not attachment:
            return ""

        return get_admin_attachment_url(attachment.pk)


def attachment_upload_path(attachment, filename):
    """
    If not defined otherwise, a content_object's attachment files will be uploaded as
    <path-to-upload-dir>/attachments/<year-and-month>/<some-uuid><extension>

    NOTE: DO NOT CHANGE THIS METHOD NAME (keep migrations sane).
    If you ever have to rename/remove this method, you need to mock it (to simply return None) in every migration
    that references to drf_attachments.storage.attachment_upload_path
    :param attachment:
    :param filename:
    :return:
    """
    filename, file_extension = os.path.splitext(filename)
    month_directory = timezone.now().strftime("%Y%m")
    return f"attachments/{month_directory}/{str(uuid1())}{file_extension}"

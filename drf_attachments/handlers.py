from django.db.models.signals import post_delete, pre_delete
from django.dispatch import receiver

from drf_attachments.models import Attachment
from drf_attachments.utils import remove_file


@receiver(pre_delete, sender=Attachment)
def remember_attachment_file_path(sender, instance, **kwargs):
    """
    Remembers the file path of an `Attachment` before it is deleted.

    The storage location of a file is derived from its content_object, which may be deleted together
    with the attachment, and can therefore no longer be resolved once the attachment is gone.
    """
    instance.file_path_to_delete = instance.file.path if instance.file else None


@receiver(post_delete, sender=Attachment)
def auto_delete_attachment_file(sender, instance, **kwargs):
    """
    Deletes file after corresponding `Attachment` object is deleted.
    """
    if instance.file_path_to_delete:
        remove_file(instance.file_path_to_delete)

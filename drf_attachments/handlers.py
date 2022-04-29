import os

from django.db.models.signals import post_delete
from django.dispatch import receiver

from drf_attachments.models import Attachment
from drf_attachments.utils import remove_file


@receiver(post_delete, sender=Attachment)
def auto_delete_attachment_file(sender, instance, **kwargs):
    """
    Deletes file after corresponding `Attachment` object is deleted.
    """
    if instance.file:
        remove_file(instance.file.path)

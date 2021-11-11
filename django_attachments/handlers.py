import os

from django.db.models.signals import post_delete
from django.dispatch import receiver

from django_attachments.models.models import Attachment


@receiver(post_delete, sender=Attachment)
def auto_delete_attachment_file(sender, instance, **kwargs):
    """
    Deletes file after corresponding `Attachment` object is deleted.
    """
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)

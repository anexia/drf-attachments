from django.db import models

from drf_attachments.models.querysets import AttachmentQuerySet

__all__ = [
    "AttachmentManager",
]


class AttachmentManager(models.Manager.from_queryset(AttachmentQuerySet)):
    use_for_related_fields = True

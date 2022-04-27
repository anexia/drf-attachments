from django.contrib.contenttypes.fields import GenericRelation

__all__ = [
    "AttachmentRelation",
]


class AttachmentRelation(GenericRelation):
    """Shortcut for a GenericRelation to attachments."""

    def __init__(self, *args, **kwargs):
        super().__init__("drf_attachments.attachment", *args, **kwargs)

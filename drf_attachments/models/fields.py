from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.db.models import FileField

__all__ = [
    "AttachmentRelation",
    "DynamicStorageFileField",
]


class AttachmentRelation(GenericRelation):
    """Shortcut for a GenericRelation to attachments."""

    def __init__(self, *args, **kwargs):
        super().__init__("drf_attachments.attachment", *args, **kwargs)


class DynamicStorageFileField(FileField):
    def pre_save(self, model_instance, add):
        meta = getattr(model_instance.content_object, "AttachmentMeta", None)
        storage_location = getattr(meta, "storage_location", settings.PRIVATE_ROOT)
        self.storage.location = storage_location
        return super().pre_save(model_instance, add)

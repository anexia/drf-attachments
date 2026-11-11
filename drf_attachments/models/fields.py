from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.db.models import FileField
from django.db.models.fields.files import FieldFile

from drf_attachments.storage import AttachmentFileStorage

__all__ = [
    "AttachmentRelation",
    "DynamicStorageFieldFile",
    "DynamicStorageFileField",
]


class AttachmentRelation(GenericRelation):
    """Shortcut for a GenericRelation to attachments."""

    def __init__(self, *args, **kwargs):
        super().__init__("drf_attachments.attachment", *args, **kwargs)


class DynamicStorageFieldFile(FieldFile):
    """
    Resolves the storage per attachment instead of sharing a single storage instance between all
    attachments of a process.

    Every attachment is stored in the AttachmentMeta.storage_location of its own content_object,
    so reading, deleting and re-saving a file always uses the location it was written to.
    """

    @property
    def storage(self):
        meta = getattr(self.instance.content_object, "AttachmentMeta", None)
        storage_location = getattr(meta, "storage_location", None) or settings.PRIVATE_ROOT
        return AttachmentFileStorage(location=storage_location)

    @storage.setter
    def storage(self, value):
        """
        Ignore the field's shared storage, which FieldFile.__init__(), FileDescriptor.__get__() and
        FieldFile.__setstate__() assign; the storage is derived from the content_object instead.
        """


class DynamicStorageFileField(FileField):
    attr_class = DynamicStorageFieldFile

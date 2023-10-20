from rest_framework import serializers
from rest_framework.fields import ChoiceField, FileField, ReadOnlyField

from drf_attachments.config import config
from drf_attachments.models.models import Attachment
from drf_attachments.rest.fields import DownloadURLField


__all__ = [
    "AttachmentSerializer",
    "AttachmentSubSerializer",
]


class AttachmentSerializer(serializers.ModelSerializer):
    """
    Attachment serializer with a `GenericRelatedField` mapping all possible models (content_types) with attachments
    to their own respective serializers.
    """

    file = FileField(write_only=True, required=True)
    content_object = config.get_content_object_field()
    context = ChoiceField(choices=config.context_choices(values_list=False))
    download_url = DownloadURLField()

    class Meta:
        model = Attachment
        fields = (
            "pk",
            "url",
            "download_url",
            "name",
            "context",
            "content_object",
            # write-only
            "file",
        )

class AttachmentSubSerializer(serializers.ModelSerializer):
    """Sub serializer for nested data inside other serializers"""

    # pk is read-only by default
    download_url = DownloadURLField()
    name = ReadOnlyField()
    context = ChoiceField(
        choices=config.context_choices(include_default=False, values_list=False),
        read_only=True,
    )

    class Meta:
        model = Attachment
        fields = (
            "pk",
            "download_url",
            "name",
            "context",
        )

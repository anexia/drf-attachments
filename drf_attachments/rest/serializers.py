from django_userforeignkey.request import get_current_request
from rest_framework import serializers
from rest_framework.fields import ChoiceField, FileField, ReadOnlyField, SerializerMethodField
from rest_framework.reverse import reverse

from drf_attachments.config import config
from drf_attachments.models.models import Attachment

__all__ = [
    "AttachmentSerializer",
    "AttachmentSubSerializer",
]


class AttachmentSerializer(serializers.ModelSerializer):
    """
    Attachment serializer with a `GenericRelatedField` mapping all possible models (content_types) with attachments
    to their own respective serializers.
    """

    download_url = SerializerMethodField(read_only=True)
    file = FileField(write_only=True, required=True)
    content_object = config.get_content_object_field()
    context = ChoiceField(choices=config.context_choices(values_list=False))

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

    def get_download_url(self, obj):
        request = get_current_request()
        relative_url = reverse("attachment-download", kwargs={"pk": obj.id})
        return request.build_absolute_uri(relative_url)


class AttachmentSubSerializer(serializers.ModelSerializer):
    """Sub serializer for nested data inside other serializers"""

    # pk is read-only by default
    download_url = SerializerMethodField(read_only=True)
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

    def get_download_url(self, obj):
        request = get_current_request()
        relative_url = reverse("attachment-download", kwargs={"pk": obj.id})
        return request.build_absolute_uri(relative_url)

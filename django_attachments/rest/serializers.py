import importlib

from django.conf import settings
from rest_framework import serializers
from rest_framework.fields import ChoiceField, FileField, ReadOnlyField

__all__ = [
    "AttachmentSerializer",
    "AttachmentSubSerializer",
]

from django_attachments.models.models import Attachment


def get_content_object_field():
    module_name, callable_name = settings.ATTACHMENT_CONTENT_OBJECT_FIELD_CALLABLE.rsplit('.', maxsplit=1)
    backend_module = importlib.import_module(module_name)
    return getattr(backend_module, callable_name)()


class AttachmentSerializer(serializers.ModelSerializer):
    """
    Attachment serializer with a `GenericRelatedField` mapping all possible models (content_types) with attachments
    to their own respective serializers.
    """

    file = FileField(write_only=True, required=True)
    content_object = get_content_object_field()

    class Meta:
        model = Attachment
        fields = (
            "pk",
            "url",
            "name",
            "context",
            "content_object",
            # write-only
            "file",
        )


class AttachmentSubSerializer(serializers.ModelSerializer):
    """ Sub serializer for nested data inside other serializers """

    # pk is read-only by default
    download_url = ReadOnlyField()
    name = ReadOnlyField()
    context = ChoiceField(choices=settings.ATTACHMENT_CONTEXT_CHOICES, read_only=True)

    class Meta:
        model = Attachment
        fields = (
            "pk",
            "download_url",
            "name",
            "context",
        )

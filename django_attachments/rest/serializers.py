from django.conf import settings
from django.utils.translation import ugettext as _
from generic_relations.relations import GenericRelatedField
from rest_framework import serializers
from rest_framework.fields import ChoiceField, FileField, ReadOnlyField

__all__ = [
    "AttachmentSerializer",
    "AttachmentSubSerializer",
]

from attachments.models.models import Attachment


class AttachmentSerializer(serializers.ModelSerializer):
    """
    Attachment serializer with a `GenericRelatedField` mapping all possible models (content_types) with attachments
    to their own respective serializers.
    """

    file = FileField(write_only=True, required=True)

    # any model with GenericRelation to Attachment must be added here to allow proper REST usage
    # make sure to use the correct view_name
    # (<model>-detail by default, if no different basename was registered in a router)
    # e.g. if `Attachment` can be related to a model `Person`:
    # content_object = GenericRelatedField(
    #     {
    #         Person: serializers.HyperlinkedRelatedField(
    #             queryset=Person.objects.all(),
    #             view_name="persons-detail",
    #         ),  # persons
    #     },
    #     help_text=_(
    #         "Unambiguous URL to a single resource (e.g. <domain>/api/v1/person/1/). "
    #         "Resources currently in use: person"
    #     ),
    # )
    content_object = GenericRelatedField(
        {},
        help_text=_(
            "Unambiguous URL to a single resource (e.g. <domain>/api/v1/<related-model>/1/). "
            "Resources currently in use: None"
        ),
    )

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

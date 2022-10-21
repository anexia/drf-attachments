from django.conf import settings
from django.utils.translation import gettext_lazy as _
from generic_relations.relations import GenericRelatedField
from rest_framework import serializers
from testapp.models import Diagram, File, PhotoAlbum, Thumbnail


def attachment_content_object_field():
    return GenericRelatedField(
        {
            PhotoAlbum: serializers.HyperlinkedRelatedField(
                queryset=PhotoAlbum.objects.all(),
                view_name="photoalbum-detail",
            ),
            Thumbnail: serializers.HyperlinkedRelatedField(
                queryset=Thumbnail.objects.all(),
                view_name="thumbnail-detail",
            ),
            Diagram: serializers.HyperlinkedRelatedField(
                queryset=Diagram.objects.all(),
                view_name="diagram-detail",
            ),
            File: serializers.HyperlinkedRelatedField(
                queryset=File.objects.all(),
                view_name="file-detail",
            ),
        },
        help_text=_(
            "Unambiguous URL to a single resource (e.g. <domain>/api/v1/<model>/1/)."
        ),
    )


def attachment_context_translations():
    return {
        settings.ATTACHMENT_CONTEXT_VACATION_PHOTO: _("Vacation Photos"),
        settings.ATTACHMENT_CONTEXT_WORK_PHOTO: _("Work Photos"),
        settings.ATTACHMENT_DEFAULT_CONTEXT: _("Attachment"),
    }


def filter_viewable_content_types(queryset):
    return queryset


def filter_editable_content_types(queryset):
    return queryset


def filter_deletable_content_types(queryset):
    return queryset

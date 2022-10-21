from rest_framework import serializers
from testapp.models import Diagram, File, PhotoAlbum, Thumbnail

from drf_attachments.rest.serializers import AttachmentSubSerializer


class PhotoAlbumSerializer(serializers.ModelSerializer):
    attachments = AttachmentSubSerializer(many=True, read_only=True)

    class Meta:
        model = PhotoAlbum
        fields = [
            "name",
            "attachments",
        ]


class ThumbnailSerializer(serializers.ModelSerializer):
    attachments = AttachmentSubSerializer(many=True, read_only=True)

    class Meta:
        model = Thumbnail
        fields = [
            "name",
            "attachments",
        ]


class DiagramSerializer(serializers.ModelSerializer):
    attachments = AttachmentSubSerializer(many=True, read_only=True)

    class Meta:
        model = Diagram
        fields = [
            "name",
            "attachments",
        ]


class FileSerializer(serializers.ModelSerializer):
    attachments = AttachmentSubSerializer(many=True, read_only=True)

    class Meta:
        model = File
        fields = [
            "name",
            "attachments",
        ]

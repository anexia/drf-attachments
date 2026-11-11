from rest_framework import serializers

from drf_attachments.rest.serializers import AttachmentSubSerializer
from testapp.models import Contract, Diagram, File, PhotoAlbum, Receipt, Thumbnail


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


class ContractSerializer(serializers.ModelSerializer):
    attachments = AttachmentSubSerializer(many=True, read_only=True)

    class Meta:
        model = Contract
        fields = [
            "name",
            "attachments",
        ]


class ReceiptSerializer(serializers.ModelSerializer):
    attachments = AttachmentSubSerializer(many=True, read_only=True)

    class Meta:
        model = Receipt
        fields = [
            "name",
            "attachments",
        ]

from django.http import FileResponse, Http404
from django_filters.rest_framework import DjangoFilterBackend
from drf_attachments.storage import AttachmentFileStorage
from drf_attachments.models.models import Attachment
from drf_attachments.rest.renderers import FileDownloadRenderer
from drf_attachments.rest.serializers import AttachmentSerializer
from rest_framework import viewsets
from rest_framework.decorators import action, parser_classes
from rest_framework.filters import SearchFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer

__all__ = [
    "AttachmentViewSet",
]


@parser_classes([MultiPartParser])
class AttachmentViewSet(viewsets.ModelViewSet):
    """Manages any attachments according to their respective content_object."""

    queryset = Attachment.objects.none()
    filter_backends = (
        DjangoFilterBackend,
        SearchFilter,
    )
    pagination_class = LimitOffsetPagination
    serializer_class = AttachmentSerializer
    permission_classes = (IsAuthenticated,)

    def get_serializer(self, *args, **kwargs):
        many = kwargs.pop("many", isinstance(kwargs.get("data"), (list, tuple)))
        return super().get_serializer(*args, many=many, **kwargs)

    def get_queryset(self):
        return Attachment.objects.viewable()

    def get_storage_path(self):
        attachment = self.get_object()
        meta = getattr(attachment.content_object, "AttachmentMeta", None)
        storage_location = getattr(meta, "storage_location", None)

        # Get custom storage location
        if meta and storage_location:
            storage = AttachmentFileStorage(location=meta.storage_location)
        else:
            # Default storage value from FileField "file"
            storage = attachment.file.storage

        # Return the file path using the appropriate storage system
        return storage.path(attachment.file.name)

    @action(
        detail=True,
        methods=["GET"],
        renderer_classes=[JSONRenderer, FileDownloadRenderer],
    )
    def download(self, request, format=None, *args, **kwargs):
        """Downloads the uploaded attachment file."""
        attachment = self.get_object()
        extension = attachment.get_extension()
        storage_path = self.get_storage_path()

        if attachment.name:
            download_file_name = f"{attachment.name}{extension}"
        else:
            download_file_name = f"attachment_{attachment.pk}{extension}"

        # Check if file exists via storage due to custom storage locations
        # without triggering SuspiciousFileOperation
        if not attachment.file.storage.exists(attachment.file.name):
            raise Http404()

        return FileResponse(
            open(storage_path, "rb"),
            as_attachment=True,
            filename=download_file_name,
        )

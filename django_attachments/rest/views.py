from rest_framework import viewsets

from django_attachments.models.models import Attachment
from django_attachments.rest.renderers import FileDownloadRenderer
from django_attachments.rest.serializers import AttachmentSerializer
from django_filters.rest_framework import DjangoFilterBackend
from django.http import FileResponse
from rest_framework.decorators import action, parser_classes
from rest_framework.filters import SearchFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer

__all__ = [
    "AttachmentViewSet",
]


def _build_download_response(attachment: Attachment):
    extension = attachment.get_extension()

    if attachment.name:
        download_file_name = f"{attachment.name}{extension}"
    else:
        download_file_name = f"attachment_{attachment.pk}{extension}"
    response = FileResponse(
        open(attachment.file.path, "rb"),
        as_attachment=True,
        filename=download_file_name,
    )

    return response


@parser_classes([MultiPartParser])
class AttachmentViewSet(viewsets.ModelViewSet):
    """ Manages any attachments according to their respective content_object. """

    queryset = Attachment.objects.none()
    filter_backends = (
        DjangoFilterBackend,
        SearchFilter,
    )
    pagination_class = LimitOffsetPagination
    serializer_class = AttachmentSerializer
    permission_classes = (IsAuthenticated,)

    def get_serializer(self, *args, **kwargs):
        many = kwargs.pop('many', isinstance(kwargs.get('data'), (list, tuple)))
        return super().get_serializer(*args, many=many, **kwargs)

    def get_queryset(self):
        return Attachment.objects.viewable()

    @action(detail=True, methods=["GET"], renderer_classes=[JSONRenderer, FileDownloadRenderer])
    def download(self, request, format=None, *args, **kwargs):
        """ Downloads the uploaded attachment file. """
        attachment = self.get_object()

        # fetch the attachment as FileResponse
        return _build_download_response(attachment)

from attachments.models.models import Attachment
from attachments.rest.renderers import FileDownloadRenderer
from attachments.rest.serializers import AttachmentSerializer
from django_filters.rest_framework import DjangoFilterBackend
from django.http import FileResponse, Http404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action, parser_classes
from rest_framework.filters import SearchFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.viewsets import GenericViewSet

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
class AttachmentViewSet(GenericViewSet):
    """ Manages any attachments according to their respective content_object. """

    queryset = Attachment.objects.none()
    filter_backends = (
        DjangoFilterBackend,
        SearchFilter,
    )
    pagination_class = LimitOffsetPagination
    serializer_class = AttachmentSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ['get', 'options', 'head']

    def get_serializer(self, *args, **kwargs):
        many = kwargs.pop('many', isinstance(kwargs.get('data'), (list, tuple)))
        return super().get_serializer(*args, many=many, **kwargs)

    def get_queryset(self):
        """ Limits the access to the currently logged-in user (according to the attachment's content_object) """
        # workaround to keep the ViewSet compatible with open api schema generation
        if self.request is None:
            return Attachment.objects.none()

        return Attachment.objects.viewable()

    # use the FileDownloadRenderer to add "type" and "format" to the openAPI schema
    @swagger_auto_schema(
        responses={
            200: openapi.Response('OK', schema=openapi.Schema(type=openapi.TYPE_FILE)),
            404: openapi.Response('Not found', schema=openapi.Schema(type=openapi.TYPE_OBJECT)),
            503: openapi.Response(
                'Service unavailable / Database unavailable',
                schema=openapi.Schema(type=openapi.TYPE_OBJECT)
            ),
        }
    )
    @action(detail=True, methods=["GET"], renderer_classes=[JSONRenderer, FileDownloadRenderer])
    def download(self, request, format=None, *args, **kwargs):
        """ Downloads the uploaded attachment file. """
        attachment = self.get_object()

        # fetch the attachment as FileResponse
        return _build_download_response(attachment)

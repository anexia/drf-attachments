from rest_framework import viewsets

from .models import Diagram, File, PhotoAlbum, Thumbnail
from .serializers import DiagramSerializer, FileSerializer, PhotoAlbumSerializer, ThumbnailSerializer


class PhotoAlbumViewSet(viewsets.ModelViewSet):
    queryset = PhotoAlbum.objects.all()
    serializer_class = PhotoAlbumSerializer


class ThumbnailViewSet(viewsets.ModelViewSet):
    queryset = Thumbnail.objects.all()
    serializer_class = ThumbnailSerializer


class DiagramViewSet(viewsets.ModelViewSet):
    queryset = Diagram.objects.all()
    serializer_class = DiagramSerializer


class FileViewSet(viewsets.ModelViewSet):
    queryset = File.objects.all()
    serializer_class = FileSerializer

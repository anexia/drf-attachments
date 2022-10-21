from django.contrib import admin
from django.urls import include, path
from rest_framework import routers
from testapp.views import (
    DiagramViewSet,
    FileViewSet,
    PhotoAlbumViewSet,
    ThumbnailViewSet,
)

from drf_attachments.rest.views import AttachmentViewSet

router = routers.DefaultRouter()
router.register(r"photo_album", PhotoAlbumViewSet)
router.register(r"thumbnail", ThumbnailViewSet)
router.register(r"diagram", DiagramViewSet)
router.register(r"file", FileViewSet)
router.register(r"attachment", AttachmentViewSet)

urlpatterns = [path("admin/", admin.site.urls), path("api/", include(router.urls))]

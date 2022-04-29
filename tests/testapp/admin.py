from django.contrib import admin

from drf_attachments.admin import AttachmentInlineAdmin
from testapp.models import Diagram, File, PhotoAlbum, Thumbnail


@admin.register(PhotoAlbum)
class PhotoAlbumAdmin(admin.ModelAdmin):
    list_display = ("name",)
    inlines = [
        AttachmentInlineAdmin,
    ]


@admin.register(Thumbnail)
class ThumbnailAdmin(admin.ModelAdmin):
    list_display = ("name",)
    inlines = [
        AttachmentInlineAdmin,
    ]


@admin.register(Diagram)
class DiagramAdmin(admin.ModelAdmin):
    list_display = ("name",)
    inlines = [
        AttachmentInlineAdmin,
    ]


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ("name",)
    inlines = [
        AttachmentInlineAdmin,
    ]

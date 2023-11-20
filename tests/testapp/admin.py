from django.contrib import admin
from testapp.models import Diagram, File, PhotoAlbum, Profile, Thumbnail

from drf_attachments.admin import AttachmentInlineAdmin, RequiredAttachmentInlineAdmin


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


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("name",)
    inlines = [
        RequiredAttachmentInlineAdmin,
    ]

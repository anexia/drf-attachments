from django.contrib.contenttypes.admin import GenericTabularInline

from django_attachments.models.models import Attachment

__all__ = [
    "AttachmentInlineAdmin",
]


class AttachmentInlineAdmin(GenericTabularInline):
    model = Attachment
    extra = 0
    fields = (
        "context",
        "name",
        "download_url",
        "file",
        "size",
        "mime_type",
        "extension",
        "creation_date",
    )
    readonly_fields = (
        "context",
        "name",
        "download_url",
        "file",
        "size",
        "mime_type",
        "extension",
        "creation_date",
    )
    show_change_link = False

    def size(self, obj):
        return obj.get_size()

    def mime_type(self, obj):
        return obj.get_mime_type()

    def extension(self, obj):
        return obj.get_extension()

    def has_add_permission(self, request, obj=None):
        return False

    class Media:
        css = {"": ("attachments/attachment_admin.css",)}

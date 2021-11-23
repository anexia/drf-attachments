from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.forms import ChoiceField, ModelForm
from django.forms.utils import ErrorList
from django.utils.translation import ugettext_lazy as _

from drf_attachments.models.models import Attachment, attachment_context_choices, attachment_context_translatable

__all__ = [
    "AttachmentInlineAdmin",
]

class AttachmentAdminMixin(object):
    def size(self, obj):
        return obj.get_size()

    def mime_type(self, obj):
        return obj.get_mime_type()

    def extension(self, obj):
        return obj.get_extension()

    def context_label(self, obj):
        return obj.context_label


class AttachmentForm(ModelForm):
    context = ChoiceField(choices=attachment_context_choices(values_list=False))


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin, AttachmentAdminMixin):
    form = AttachmentForm
    list_display = ["pk", "name", "content_object", "context_label"]
    fields = (
        "name",
        "context",
        "content_type",
        "object_id",
        "file",
        "size",
        "mime_type",
        "extension",
        "creation_date",
    )
    readonly_fields = (
        "size",
        "mime_type",
        "extension",
        "creation_date",
    )


class AttachmentInlineAdmin(GenericTabularInline, AttachmentAdminMixin):
    model = Attachment
    extra = 0
    fields = (
        "context_label",
        "name",
        "download_url",
        "file",
        "size",
        "mime_type",
        "extension",
        "creation_date",
    )
    readonly_fields = (
        "context_label",
        "name",
        "download_url",
        "file",
        "size",
        "mime_type",
        "extension",
        "creation_date",
    )
    show_change_link = False

    def has_add_permission(self, request, obj=None):
        return False

    class Media:
        css = {"": ("attachments/attachment_admin.css",)}

from content_disposition import rfc5987_content_disposition
from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.contenttypes.admin import GenericTabularInline
from django.forms import ChoiceField, ModelForm
from django.http import StreamingHttpResponse
from django.urls import NoReverseMatch, reverse, path
from django.utils.safestring import mark_safe

from drf_attachments.config import config
from drf_attachments.models.models import Attachment

__all__ = [
    "AttachmentInlineAdmin",
]


class AttachmentAdminMixin(object):
    @staticmethod
    def size(obj):
        return obj.get_size()

    @staticmethod
    def mime_type(obj):
        return obj.get_mime_type()

    @staticmethod
    def extension(obj):
        return obj.get_extension()

    @staticmethod
    def context_label(obj):
        return obj.context_label


class AttachmentForm(ModelForm):
    context = ChoiceField(choices=config.context_choices(values_list=False))


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin, AttachmentAdminMixin):
    form = AttachmentForm
    list_display = ["pk", "name", "content_object", "context_label"]
    fields = (
        "name",
        "context",
        "content_type",
        "object_id",
        "content_object",
        "file",
        "size",
        "mime_type",
        "extension",
        "creation_date",
    )
    readonly_fields = (
        "content_object",
        "size",
        "mime_type",
        "extension",
        "creation_date",
    )

    @staticmethod
    def content_object(obj):
        entity = obj.content_object
        app_label = entity._meta.app_label
        model_name = entity._meta.model_name
        try:
            admin_url = reverse(
                f"admin:{app_label}_{model_name}_change", args=(entity.pk,)
            )
            return mark_safe(f'<a href="{admin_url}">{entity}</a>')
        except NoReverseMatch:
            return entity

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "<path:object_id>/download/",
                self.admin_site.admin_view(self.download_view),
                name="drf_attachments_attachment_download"
            ),
        ]
        return custom_urls + urls

    def download_view(self, request, object_id):
        attachment = Attachment.objects.get(pk=object_id)
        response = StreamingHttpResponse(
            attachment.file,
            content_type=attachment.get_mime_type(),
        )
        response["Content-Disposition"] = rfc5987_content_disposition(
            (attachment.name if attachment.name else str(attachment.pk)) + attachment.get_extension()
        )

        return response


class BaseAttachmentInlineAdmin(GenericTabularInline, AttachmentAdminMixin):
    model = Attachment
    form = AttachmentForm
    extra = 0
    fields = (
        "name",
        "context",
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


class AttachmentInlineAdmin(BaseAttachmentInlineAdmin):
    def has_change_permission(self, request, obj=None):
        return False

    show_change_link = True


class ReadOnlyAttachmentInlineAdmin(AttachmentInlineAdmin):
    def has_add_permission(self, request, obj=None):
        return False

    show_change_link = False

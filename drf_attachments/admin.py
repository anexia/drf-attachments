from content_disposition import rfc5987_content_disposition
from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.contrib.contenttypes.forms import BaseGenericInlineFormSet
from django.forms import ChoiceField, ModelForm
from django.forms.utils import ErrorList
from django.http import StreamingHttpResponse
from django.urls import NoReverseMatch, path, reverse
from django.utils.safestring import mark_safe

from drf_attachments.config import config
from drf_attachments.models.models import Attachment

__all__ = [
    "AttachmentInlineAdmin",
    "RequiredAttachmentInlineAdmin",
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
        "meta",
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

    def get_object(self, request, object_id, from_field=None):
        obj = super().get_object(request, object_id, from_field)

        # handling missing file (e.g. file may have been deleted on the server)
        if not obj.file.storage.exists(obj.file.name):
            self.message_user(request, "File not found", level="ERROR")
            obj.file = None

        return obj

    @staticmethod
    def content_object(obj):
        entity = obj.content_object

        if entity:
            app_label = entity._meta.app_label
            model_name = entity._meta.model_name

            try:
                admin_url = reverse(
                    f"admin:{app_label}_{model_name}_change", args=(entity.pk,)
                )
                return mark_safe(f'<a href="{admin_url}">{entity}</a>')
            except NoReverseMatch:
                return entity

        return "not found (change object_id or content_type)"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "<path:object_id>/download/",
                self.admin_site.admin_view(self.download_view),
                name="drf_attachments_attachment_download",
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
            (attachment.name if attachment.name else str(attachment.pk))
            + attachment.get_extension()
        )

        return response


class DynamicallyDisabledAttachmentInlineForm(AttachmentForm):
    class Meta:
        model = Attachment
        fields = "__all__"

    def disable_inline_fields(self):
        """
        Override to return True/False when custom condition is met
        and change field readonly status in inline admin list on True
        """
        raise NotImplementedError()

    def __init__(
        self,
        data=None,
        files=None,
        auto_id="id_%s",
        prefix=None,
        initial=None,
        error_class=ErrorList,
        label_suffix=None,
        empty_permitted=False,
        instance=None,
        use_required_attribute=None,
        renderer=None,
    ):
        super().__init__(
            data,
            files,
            auto_id,
            prefix,
            initial,
            error_class,
            label_suffix,
            empty_permitted,
            instance,
            use_required_attribute,
            renderer,
        )

        # make all fields of the inline attachment read only
        if self.disable_inline_fields():
            for field in self.fields:
                self.fields[field].disabled = True


class DynamicallyDisabledAttachmentInlineFormSet(BaseGenericInlineFormSet):
    def add_fields(self, form, index):
        """
        Disables the DELETE checkbox of disabled inline entries.
        """
        super().add_fields(form, index)
        if hasattr(form, 'disable_inline_fields') and form.disable_inline_fields():
            form.fields['DELETE'].disabled = True


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
        "last_modification_date",
    )
    readonly_fields = (
        "size",
        "mime_type",
        "extension",
        "creation_date",
        "last_modification_date",
    )


class AttachmentInlineAdmin(BaseAttachmentInlineAdmin):
    def has_change_permission(self, request, obj=None):
        return False

    show_change_link = True


class ReadOnlyAttachmentInlineAdmin(AttachmentInlineAdmin):
    def has_add_permission(self, request, obj=None):
        return False

    show_change_link = False


class RequiredAttachmentInlineAdmin(AttachmentInlineAdmin):
    min_num = 1

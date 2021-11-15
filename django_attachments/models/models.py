import os
import uuid
from uuid import uuid1

from django_attachments.models.managers import AttachmentManager
from django_attachments.uitls import get_mime_type, get_extension, remove
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import JSONField
from django.core.files.storage import FileSystemStorage
from django.db.models import CASCADE, CharField, DateTimeField, FileField, ForeignKey, Model, UUIDField
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django_userforeignkey.request import get_current_request
from rest_framework.exceptions import ValidationError
from rest_framework.reverse import reverse

__all__ = [
    "Attachment",
]


class AttachmentFileStorage(FileSystemStorage):
    """
    This is used to store attachments in a folder that is not mode publicly available by the webserver
    Attachments are served with a dedicated API route instead
    """
    def __init__(self):
        super().__init__(location=settings.PRIVATE_ROOT)


def attachment_upload_path(attachment, filename):
    """
    If not defined otherwise, a content_object's attachment files will be uploaded as
    <path-to-upload-dir>/attachments/<year-and-month>/<some-uuid><extension>

    NOTE: DO NOT CHANGE THIS METHOD NAME (keep migrations sane).
    If you ever have to rename/remove this method, you need to mock it (to simply return None) in every migration
    that references to django_attachments.models.models.attachment_upload_path
    :param attachment:
    :param filename:
    :return:
    """
    filename, file_extension = os.path.splitext(filename)
    month_directory = timezone.now().strftime("%Y%m")
    return f"attachments/{month_directory}/{str(uuid1())}{file_extension}"


class Attachment(Model):
    """
    Attachments accept any other Model as content_object and store the uploaded files in their respective directories
    (if not defined otherwise in attachment_upload_path)
    """

    objects = AttachmentManager()

    id = UUIDField(
        _('Attachment ID'),
        default=uuid.uuid4,
        editable=False,
        unique=True,
        primary_key=True,
    )

    name = CharField(
        _("name"),
        max_length=255,
        blank=True,
    )

    context = CharField(
        _("context"),
        help_text=_("Additional info about the attachment's context/meaning."),
        max_length=255,
        blank=True,
    )

    meta = JSONField(
        _("meta"),
        help_text=_("Additional info about the attachment (e.g. file meta data: mime_type, extension, size)."),
        blank=False,
        null=False,
    )

    file = FileField(
        verbose_name=_("file"),
        upload_to=attachment_upload_path,  # DO NOT CHANGE UPLOAD METHOD NAME (keep migrations sane)
        storage=AttachmentFileStorage(),
    )

    # Generic Relation (to add one of multiple different models/content types to an attachment)
    content_type = ForeignKey(ContentType, on_delete=CASCADE)
    object_id = UUIDField()
    content_object = GenericForeignKey()

    creation_date = DateTimeField(
        verbose_name=_(u"Creation date"),
        blank=False,
        null=False,
        auto_now_add=True,
    )

    last_modification_date = DateTimeField(
        verbose_name=_(u"Last modification date"),
        blank=False,
        null=False,
        auto_now=True,
    )

    class Meta:
        verbose_name = _("attachment")
        verbose_name_plural = _("attachments")
        ordering = ("creation_date",)

    def __str__(self):
        return f"{self.content_type} | {self.object_id} | {self.context} | {self.name}"

    @property
    def is_image(self):
        return 'mime_type' in self.meta and self.meta['mime_type'] and self.meta['mime_type'].startswith("image")

    @property
    def download_url(self):
        request = get_current_request()
        relative_url = reverse("attachment-download", kwargs={"pk": self.id})
        return request.build_absolute_uri(relative_url)

    @property
    def valid_contexts(self):
        return [x[0] for x in settings.ATTACHMENT_CONTEXT_CHOICES]

    def is_modified(self):
        return self.creation_date != self.last_modification_date

    def get_extension(self):
        return self.meta.get('extension')

    def get_size(self):
        return self.meta.get('size')

    def get_mime_type(self):
        return self.meta.get('mime_type')

    def save(self, *args, **kwargs):
        # set computed values for direct and API access
        self.set_default_context()
        self.set_attachment_meta()  # read the AttachmentMeta settings from the content_object's model
        self.set_file_meta()  # extract and store mime_type, extension and size from the current file
        super().save(*args, **kwargs)

    def clean(self):
        super().clean()

        # set computed values for form checks (Django admin)
        self.set_default_context()
        self.set_attachment_meta()  # read the AttachmentMeta settings from the content_object's model
        self.set_file_meta()  # extract and store mime_type, extension and size from the current file

        self.validate_context()  # validate that the context is allowed
        self.validate_file()  # validate the file and its mime_type, extension and size
        self.manage_uniqueness()  # remove any other Attachments for content_objects with
        self.cleanup_file()  # remove the old file of a changed Attachment

    def set_default_context(self):
        """ Set context to settings.ATTACHMENT_DEFAULT_CONTEXT (if defined) if it's still empty """
        if not self.context and hasattr(settings, 'ATTACHMENT_DEFAULT_CONTEXT'):
            self.context = settings.ATTACHMENT_DEFAULT_CONTEXT

    def set_attachment_meta(self):
        meta = getattr(self.content_object, "AttachmentMeta", None)
        self.valid_mime_types = getattr(meta, "valid_mime_types", None)
        self.valid_extensions = getattr(meta, "valid_extensions", None)
        self.min_size = int(getattr(meta, "min_size", 0))
        self.max_size = min(
            int(getattr(meta, "max_size", settings.ATTACHMENT_MAX_UPLOAD_SIZE)),
            int(settings.ATTACHMENT_MAX_UPLOAD_SIZE),
        )
        self.unique_upload = getattr(meta, "unique_upload", False)
        self.unique_upload_per_context = getattr(meta, "unique_upload_per_context", False)

    def set_file_meta(self):
        if self.meta is None:
            self.meta = {}
        self.meta['mime_type'] = get_mime_type(self.file)
        self.meta['extension'] = get_extension(self.file)
        self.meta['size'] = self.file.size

    def validate_context(self):
        """
        Make sure the given context is allowed by the settings/configs
        :return:
        """
        if self.context and self.context not in self.valid_contexts:
            error_msg = _(
                "Invalid context {context} detected! It must be one of the following: {valid_contexts}"
            ).format(
                context=self.context,
                valid_contexts=", ".join(self.valid_contexts),
            )
            raise ValidationError(
                {
                    "context": error_msg,
                },
                code="invalid",
            )

    def validate_file(self):
        """
        Make sure the given file has the expected mime_type and extension
        :return:
        """
        # validate mime type
        self._validate_file_mime_type()

        # validate extension
        self._validate_file_extension()

        # validate file size
        self._validate_file_size()

    def _validate_file_mime_type(self):
        """
        Validate the mime_type against the AttachmentMeta.valid_mime_types defined in the content_object's model class.
        Raise a ValidationError on failure.
        :return:
        """
        if self.valid_mime_types and self.meta['mime_type'] not in self.valid_mime_types:
            error_msg = _(
                "Invalid mime type {mime_type} detected! It must be one of the following: {valid_mime_types}"
            ).format(
                mime_type=self.meta['mime_type'],
                valid_mime_types=", ".join(self.valid_mime_types),
            )
            raise ValidationError(
                {
                    "file": error_msg,
                },
                code="invalid",
            )

    def _validate_file_extension(self):
        """
        Validate the extension against the AttachmentMeta.valid_extensions defined in the content_object's model class.
        Raise a ValidationError on failure.
        :return:
        """
        if self.valid_extensions and self.meta['extension'] not in self.valid_extensions:
            error_msg = _(
                "Invalid extension {extension} detected! It must be one of the following: {valid_extensions}"
            ).format(
                extension=self.meta['extension'],
                valid_extensions=", ".join(self.valid_extensions),
            )
            raise ValidationError(
                {
                    "file": error_msg,
                },
                code="invalid",
            )

    def _validate_file_size(self):
        """
        Validate the size against the AttachmentMeta.min_size and AttachmentMeta.max_size defined in the
        content_object's model class.
        The maximum allowed file size is always restricted by settings.ATTACHMENT_MAX_UPLOAD_SIZE.
        Validate the extension and raise a ValidationError on failure.
        :return:
        """
        if self.min_size and self.file.size < self.min_size:
            error_msg = _("File size {size} too small! It must be at least {min_size}").format(
                size=self.file.size,
                min_size=self.min_size,
            )
            raise ValidationError(
                {
                    "file": error_msg,
                },
                code="invalid",
            )

        # self.max_size is always given (settings.ATTACHMENT_MAX_UPLOAD_SIZE by default and as maximum)
        if self.file.size > self.max_size:
            error_msg = _("File size {size} too large! It can only be {max_size}").format(
                size=self.file.size,
                max_size=self.max_size,
            )
            raise ValidationError(
                {
                    "file": error_msg,
                },
                code="invalid",
            )

    def manage_uniqueness(self):
        """
        If the content_object defines "unique_upload=True", only keep a single Attachment for it
        ("unique_upload_per_context" config will be ignored). Remove any previous/other attachments and delete their
        files from the storage.
        If the content_object defines "unique_upload_per_context=True", only keep a single Attachment per context
        ("unique_upload" must be set to "False" for this to work). Remove any previous/other attachments with the same
        context and delete their files from the storage.
        :return:
        """
        to_delete = None

        if self.unique_upload:
            # delete any previous/other existing Attachments of the content_object (keep only the current one)
            to_delete = Attachment.objects.filter(
                object_id=self.content_object.pk,
                content_type=ContentType.objects.get_for_model(self.content_object).pk,
            )
            if self.pk:
                to_delete = to_delete.exclude(pk=self.pk)
        elif self.unique_upload_per_context:
            # delete any previous/other existing Attachments of the content_object (keep only the current one)
            to_delete = Attachment.objects.filter(
                object_id=self.content_object.pk,
                content_type=ContentType.objects.get_for_model(self.content_object).pk,
                context=self.context,
            )
            if self.pk:
                to_delete = to_delete.exclude(pk=self.pk)

        if to_delete:
            for attachment in to_delete:
                remove(attachment.file)

            to_delete.delete()

    def cleanup_file(self):
        """
        If an Attachment is updated and receives a new file, remove the previous file from the storage
        :return:
        """
        if self.pk:
            # on update delete the old file if a new one was inserted
            # (delete_orphan only removes image on deletion of the whole attachment instance)
            old_instance = Attachment.objects.get(pk=self.pk)

            # on update delete the old file if a new one was inserted
            if old_instance.file != self.file:
                remove(old_instance.file)

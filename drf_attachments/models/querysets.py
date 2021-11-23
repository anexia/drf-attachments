import importlib
import os

from django.conf import settings
from django.db.models.query import QuerySet

__all__ = [
    "AttachmentQuerySet",
]


def filter_viewable_content_types(queryset):
    module_name, callable_name = settings.ATTACHMENT_FILTER_VIEWABLE_CONTENT_OBJECTS_CALLABLE.rsplit('.', maxsplit=1)
    backend_module = importlib.import_module(module_name)
    return getattr(backend_module, callable_name)(queryset)


def filter_editable_content_types(queryset):
    module_name, callable_name = settings.ATTACHMENT_FILTER_EDITABLE_CONTENT_OBJECTS_CALLABLE.rsplit('.', maxsplit=1)
    backend_module = importlib.import_module(module_name)
    return getattr(backend_module, callable_name)(queryset)


def filter_deletable_content_types(queryset):
    module_name, callable_name = settings.ATTACHMENT_FILTER_DELETABLE_CONTENT_OBJECTS_CALLABLE.rsplit('.', maxsplit=1)
    backend_module = importlib.import_module(module_name)
    return getattr(backend_module, callable_name)(queryset)


class AttachmentQuerySet(QuerySet):
    """
    Any model with GenericRelation to Attachment must be added
    to all relevant queryset methods to allow proper access
    """
    def viewable(self, *args, **kwargs):
        return filter_viewable_content_types(self)

    def editable(self, *args, **kwargs):
        return filter_editable_content_types(self)

    def deletable(self, *args, **kwargs):
        return filter_deletable_content_types(self)

    def delete(self):
        """
        Bulk remove files after related Attachments were deleted
        """
        files = list(self.values_list('file', flat=True))
        result = super().delete()

        # remove all files that belonged to the deleted attachments
        for file in files:
            path = f"{settings.MEDIA_ROOT}/{file}"
            if os.path.isfile(path):
                try:
                    os.remove(path)
                except:
                    pass

        return result

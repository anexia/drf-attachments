from django.conf import settings
from django.db.models.query import QuerySet

from drf_attachments.config import config
from drf_attachments.utils import remove_file

__all__ = [
    "AttachmentQuerySet",
]


class AttachmentQuerySet(QuerySet):
    def viewable(self, *args, **kwargs):
        callable_ = config.get_filter_callable_for_viewable_content_objects()
        return self.__filter_by_callable(callable_)

    def editable(self, *args, **kwargs):
        callable_ = config.get_filter_callable_for_editable_content_objects()
        return self.__filter_by_callable(callable_)

    def deletable(self, *args, **kwargs):
        callable_ = config.get_filter_callable_for_deletable_content_objects()
        return self.__filter_by_callable(callable_)

    def delete(self):
        """Bulk remove files after related Attachments were deleted"""
        files = list(self.values_list("file", flat=True))
        result = super().delete()

        # remove all files that belonged to the deleted attachments
        for file in files:
            path = f"{settings.MEDIA_ROOT}/{file}"
            remove_file(path)

        return result

    def __filter_by_callable(self, callable_) -> QuerySet:
        if callable_:
            return callable_(self)
        else:
            return self

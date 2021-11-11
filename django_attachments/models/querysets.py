import os

from django.conf import settings
from django.db.models.query import QuerySet

__all__ = [
    "AttachmentQuerySet",
]

from django_userforeignkey.request import get_current_user


def filter_viewable_content_types(queryset, orig_queryset):
    """
    Override to return viewable related content_types.

    """
    return queryset


class AttachmentQuerySet(QuerySet):
    """
    Any model with GenericRelation to Attachment must be added
    to all relevant queryset methods to allow proper access
    """
    def viewable(self, *args, **kwargs):
        """
        Todo: Extend permission checks
        """
        user = get_current_user()
        if user.is_superuser:
            return self.all()
        return self.none()

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

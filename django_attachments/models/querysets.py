import os

from django.conf import settings
from django.db.models.query import QuerySet

__all__ = [
    "AttachmentQuerySet",
]


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
        Override for model specific filtering
        Show only attachments of content_objects belonging to the logged-in user.
        E.g. if `Attachment` can be related to a model `users.UserVehicle`:
            def viewable(self, *args, **kwargs):
                queryset = super().viewable(*args, **kwargs)

                from django_userforeignkey.request import get_current_user
                user = get_current_user()
                if not user.is_superuser:
                    from <project-name>.users.models import UserVehicle
                    # user may only see attachments of UserVehicles they may view
                    viewable_vehicles = UserVehicle.objects.viewable()
                    queryset = queryset.filter(users_uservehicles__in=viewable_vehicles)

                return queryset

        :param args:
        :param kwargs:
        :return:
        """
        return super().viewable(*args, **kwargs)

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

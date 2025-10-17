from django.urls import reverse

from rest_framework import serializers

__all__ = [
    "DownloadURLField",
]


class DownloadURLField(serializers.Field):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("read_only", True)
        super().__init__(*args, **kwargs)

    def get_attribute(self, instance):
        request = self.context.get("request")
        relative_url = reverse("attachment-download", kwargs={"pk": instance.pk})

        if request is None:
            return relative_url
        return request.build_absolute_uri(relative_url)

    def to_representation(self, value):
        return value

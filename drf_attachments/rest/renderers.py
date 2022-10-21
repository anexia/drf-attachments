from rest_framework.renderers import BaseRenderer

__all__ = [
    "FileDownloadRenderer",
]


class FileDownloadRenderer(BaseRenderer):
    """Return data as download/attachment."""

    media_type = "application/octet-stream"
    format = "binary"
    type = "string"

    def render(self, data, accepted_media_type=None, renderer_context=None):
        return data

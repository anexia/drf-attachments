from django.apps import apps
from django.conf import settings
from django.test import SimpleTestCase
from testapp.models import PhotoAlbum

from drf_attachments.models import Attachment


class TestSetup(SimpleTestCase):
    def test_installed_apps(self):
        self.assertIn("drf_attachments", settings.INSTALLED_APPS)

    def test_models(self):
        self.assertIs(apps.get_model("drf_attachments", "Attachment"), Attachment)
        self.assertIs(apps.get_model("testapp", "PhotoAlbum"), PhotoAlbum)

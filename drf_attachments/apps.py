from django.apps import AppConfig
from django.conf import settings
from django.contrib.auth.management import create_permissions
from django.db.models.signals import post_migrate
from django.utils.translation import gettext_lazy as _


def create_global_permissions_for_app(sender, **kwargs):
    # App is set by sender in post migrate
    app = sender
    # Add view permission to all models of this app
    for model_class in app.models.values():
        model_meta = model_class._meta

        global_permissions = getattr(settings, "GLOBAL_MODEL_PERMISSIONS", [])
        for permission in global_permissions:
            if permission not in model_meta.default_permissions:
                model_meta.default_permissions += (permission,)

    create_permissions(app)


class AttachmentsConfig(AppConfig):
    name = "drf_attachments"
    verbose_name = _("attachments")

    def ready(self):
        post_migrate.connect(create_global_permissions_for_app, sender=self)

        # import signal handlers
        import drf_attachments.handlers

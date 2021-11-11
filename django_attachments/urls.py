from rest_framework import routers
from attachments.rest.views import AttachmentViewSet

router = routers.DefaultRouter()

router.register(r"attachment", AttachmentViewSet)

urlpatterns = []

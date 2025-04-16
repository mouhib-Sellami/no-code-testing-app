from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static
from rest_framework.routers import SimpleRouter
from app_backend.viewSets.ProjectModelViewSet import ProjectModelViewSet
from app_backend.viewSets.PermissionViewSet import PermissionViewSet

router = SimpleRouter()
router.register(r"projects", ProjectModelViewSet, basename="projects")
router.register(r"permissions", PermissionViewSet, basename="permission")

urlpatterns = [
    path("", include(router.urls)),
] + static(settings.MEDIA_URL,
           document_root=settings.MEDIA_ROOT)

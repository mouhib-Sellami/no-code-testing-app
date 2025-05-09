from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static
from rest_framework.routers import SimpleRouter
from app_backend.viewSets.ProjectModelViewSet import ProjectModelViewSet
from app_backend.viewSets.PermissionViewSet import PermissionViewSet
from app_backend.viewSets.RoleModelViewSet import RoleModelViewSet
from app_backend.viewSets.UserModelViewSet import UserModelViewSet

router = SimpleRouter()
router.register(r"projects", ProjectModelViewSet, basename="projects")
router.register(r"permissions", PermissionViewSet, basename="permissions")
router.register(r"roles", RoleModelViewSet, basename="roles")
router.register(r"users", UserModelViewSet, basename="users")

urlpatterns = [
    path("", include(router.urls)),
] + static(settings.MEDIA_URL,
           document_root=settings.MEDIA_ROOT)

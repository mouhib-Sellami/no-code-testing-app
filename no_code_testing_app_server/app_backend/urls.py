from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static
from rest_framework.routers import SimpleRouter
from app_backend.viewSets.ProjectModelViewSet import ProjectModelViewSet
from app_backend.viewSets.PermissionViewSet import PermissionViewSet
from app_backend.viewSets.RoleModelViewSet import RoleModelViewSet
from app_backend.viewSets.UserModelViewSet import UserModelViewSet
from app_backend.viewSets.ProjectComponentViewSet import ProjectComponentViewSet
from app_backend.viewSets.EdgesViewSet import EdgesViewSet
from app_backend.viewSets.ProjectLogViewSet import ProjectLogViewSet

router = SimpleRouter()
router.register(r"projects", ProjectModelViewSet, basename="projects")
router.register(r"projects-components", ProjectComponentViewSet,
                basename="projects-components")
router.register(r"edges", EdgesViewSet,
                basename="edges")
router.register(r"permissions", PermissionViewSet, basename="permissions")
router.register(r"roles", RoleModelViewSet, basename="roles")
router.register(r"users", UserModelViewSet, basename="users")
router.register(r"project-logs", ProjectLogViewSet, basename="project-logs")

urlpatterns = [
    path("", include(router.urls)),
] + static(settings.MEDIA_URL,
           document_root=settings.MEDIA_ROOT)

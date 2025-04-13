from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static
from rest_framework.routers import SimpleRouter
from app_tenant.viewSets.DomainViewSet import DomainViewSet

router = SimpleRouter()
router.register(r"domains", DomainViewSet, basename="domains")

urlpatterns = [
    path("", include(router.urls)),
] + static(settings.MEDIA_URL,
           document_root=settings.MEDIA_ROOT)

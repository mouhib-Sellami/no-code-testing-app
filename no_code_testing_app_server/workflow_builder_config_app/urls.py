from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static
from rest_framework.routers import SimpleRouter
from workflow_builder_config_app.viewsets.ProvidersReadOnlyViewSet import ProvidersReadOnlyViewSet
router = SimpleRouter()
router.register(r"providers", ProvidersReadOnlyViewSet, basename="providers")

urlpatterns = [
    path("", include(router.urls)),
] + static(settings.MEDIA_URL,
           document_root=settings.MEDIA_ROOT)

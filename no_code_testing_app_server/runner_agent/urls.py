from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static
from rest_framework.routers import SimpleRouter
from runner_agent.viewSets.RunnerModelViewSet import RunnerModelViewSet
from runner_agent.viewSets.RunnerActionViewSet import RunnerActionViewSet

router = SimpleRouter()
router.register(r"runner-agents", RunnerModelViewSet, basename="runner-agents")
router.register(r"runner-agent-actions", RunnerActionViewSet,
                basename="runner-agent-actions")

urlpatterns = [
    path("", include(router.urls)),
] + static(settings.MEDIA_URL,
           document_root=settings.MEDIA_ROOT)

from app_backend import serializers, models
from rest_framework.viewsets import GenericViewSet, mixins
from rest_framework.permissions import IsAuthenticated
import logging

logger = logging.getLogger('no_code_testing_app')
CONTENT_TYPE = "application/json"


class ProjectTestViewSet(GenericViewSet, mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin, mixins.UpdateModelMixin):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.ProjectTestCaseSerializer
    queryset = models.ProjectTestCase.objects.all()

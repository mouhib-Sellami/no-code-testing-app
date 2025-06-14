from app_backend import serializers, models
from rest_framework.viewsets import GenericViewSet, mixins
from rest_framework.permissions import IsAuthenticated
import logging
from rest_framework.decorators import action
from django.http import HttpResponse
from rest_framework import status
import json
logger = logging.getLogger('no_code_testing_app')
CONTENT_TYPE = "application/json"


class ProjectTestViewSet(GenericViewSet, mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin, mixins.UpdateModelMixin):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.ProjectTestCaseSerializer
    queryset = models.ProjectTestCase.objects.all()

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @action(url_name="components", detail=True, url_path="components", serializer_class=serializers.ProjectComponentSerializer)
    def test_components(self, request, pk=None):
        try:
            components = models.ProjectComponent.objects.filter(
                project_test_case__id=pk).all()
            print(components)
            return HttpResponse(json.dumps(serializers.ProjectComponentSerializer(components, many=True).data), status=status.HTTP_200_OK, content_type=CONTENT_TYPE)
        except Exception as e:
            logger.exception(str(e))
            return HttpResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, content_type=CONTENT_TYPE)

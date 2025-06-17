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


class ProjectWorkFlowsViewSet(GenericViewSet, mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin, mixins.UpdateModelMixin):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.ProjectTestFlowSerializer
    queryset = models.ProjectTestFlow.objects.all()

    @action(url_name="get-components", detail=True, url_path="components", serializer_class=serializers.TestFlowComponentSerializer, methods=['GET'])
    def flow_components(self, request, pk=None):
        try:
            cases = models.TestFlowComponent.objects.filter(
                test_flow__id=pk).all()
            return HttpResponse(json.dumps(serializers.TestFlowComponentSerializer(cases, many=True).data), status=status.HTTP_200_OK, content_type=CONTENT_TYPE)
        except Exception as e:
            logger.exception(str(e))
            return HttpResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, content_type=CONTENT_TYPE)


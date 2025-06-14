from app_backend import serializers, models
from rest_framework.viewsets import GenericViewSet, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
import logging
import json
from rest_framework import status
from django.http import HttpResponse
from app_backend import serializers, models
from rest_framework.decorators import action


logger = logging.getLogger('no_code_testing_app')
CONTENT_TYPE = "application/json"


class EdgesViewSet(GenericViewSet, mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin, mixins.UpdateModelMixin):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.EdgeSerializer
    queryset = models.ComponentDependency.objects.all()
    
    def retrieve(self, request, pk=None, *args, **kwargs):
        try:
            edges = models.ComponentDependency.objects.filter(
                Q(source_component__project_test_case__id=pk) |
                Q(target_component__project_test_case__id=pk)
            )
            return HttpResponse(json.dumps(serializers.EdgeSerializer(edges, many=True).data), status=status.HTTP_200_OK, content_type=CONTENT_TYPE)
        except Exception as e:
            logger.exception(str(e))
            return HttpResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, content_type=CONTENT_TYPE)
    
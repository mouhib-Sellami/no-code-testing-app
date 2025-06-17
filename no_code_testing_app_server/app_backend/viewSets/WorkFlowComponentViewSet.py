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


class WorkFlowComponentViewSet(GenericViewSet, mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin, mixins.UpdateModelMixin):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.TestFlowComponentSerializer
    queryset = models.TestFlowComponent.objects.all()

    def get_serializer_class(self):
        if self.action in ['create']:
            return serializers.CreateTestFlowComponentSerializer
        return serializers.TestFlowComponentSerializer

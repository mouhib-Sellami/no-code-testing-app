import logging
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from . import serializers
from rest_framework.permissions import IsAuthenticated
from app_backend import models

logger = logging.getLogger('sky_forge')
CONTENT_TYPE = 'application/json'

class ProjectModelViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.ProjectSerializer
    queryset = models.Project.objects.all()
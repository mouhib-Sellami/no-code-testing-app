import json
import logging
from rest_framework import status
from django.http import HttpResponse
from app_backend import serializers, models
from rest_framework.decorators import action
from no_code_testing_app_server.shared.ViewSetsPagination import CustomPaginator
from app_user_auth.auth_decorators.decorators import has_permission
from rest_framework.viewsets import ReadOnlyModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

logger = logging.getLogger('no_code_testing_app')
CONTENT_TYPE = "application/json"


class ProjectLogViewSet(ReadOnlyModelViewSet):
    serializer_class = serializers.ProjectStatusLogSerializer
    queryset = models.ProjectStatusLog.objects.all().order_by("-updated_at")
    pagination_class = CustomPaginator

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["project",]

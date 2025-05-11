import logging
from . import serializers
from app_backend import models
from rest_framework import filters
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from app_user_auth.auth_decorators.decorators import has_permission
from app_backend.pagination_filters.app_pagination import defaultPagination

logger = logging.getLogger('no_code_testing_app')
CONTENT_TYPE = 'application/json'


class ProjectModelViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.ProjectSerializer
    queryset = models.Project.objects.all()

    pagination_class = defaultPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]

    search_fields = ["$name",
                     "$managed_by__user__username", '$provider__name']

    @has_permission("can_view_all_project")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @has_permission("can_create_project")
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @has_permission("can_change_project")
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @has_permission("can_delete_project")
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @has_permission("can_view_project")
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @has_permission("can_change_project")
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

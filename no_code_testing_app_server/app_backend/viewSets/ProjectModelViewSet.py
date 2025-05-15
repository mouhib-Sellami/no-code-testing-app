import json
import logging
from rest_framework import status
from django.http import HttpResponse
from app_backend import serializers, models
from rest_framework.decorators import action
from app_user_auth.auth_decorators.decorators import has_permission
from no_code_testing_app_server.shared import BaseModelViewSet

logger = logging.getLogger('no_code_testing_app')
CONTENT_TYPE = "application/json"


class ProjectModelViewSet(BaseModelViewSet):
    serializer_class = serializers.ProjectSerializer
    queryset = models.Project.objects.all()

    search_fields = ["$name",
                     "$managed_by__user__username", '$provider__name']

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return serializers.ProjectSerializer
        return serializers.CreateProjectSerializer

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

    @has_permission("can_view_all_project")
    @action(methods=['GET'], url_path="recent", url_name="recent", detail=False, serializer_class=serializers.ProjectSerializer)
    def recent(self, request, *args, **kwargs):
        try:
            projects = models.Project.objects.all().order_by('-updated_at')[:5]
            return HttpResponse(json.dumps(serializers.ProjectSerializer(projects, many=True).data), status=status.HTTP_200_OK, content_type=CONTENT_TYPE)
        except Exception as e:
            logger.exception(str(e))
            return HttpResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, content_type=CONTENT_TYPE)

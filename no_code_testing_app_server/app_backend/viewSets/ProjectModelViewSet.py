import json
import logging
from rest_framework import status
from django.http import HttpResponse
from app_backend import serializers, models
from rest_framework.decorators import action
from app_user_auth.auth_decorators.decorators import has_permission
from no_code_testing_app_server.shared import BaseModelViewSet
from django.core.exceptions import ObjectDoesNotExist
from no_code_testing_app_server.utils.MqttClient import MQTTClient
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

    @has_permission("can_change_project")
    @action(methods=['GET'], url_path="components", url_name="components", detail=True, serializer_class=serializers.ProjectComponentSerializer)
    def components(self, request, pk=None, *args, **kwargs):
        try:
            components = models.ProjectComponent.objects.filter(
                project__id=pk).all()
            return HttpResponse(json.dumps(serializers.ProjectComponentSerializer(components, many=True).data), status=status.HTTP_200_OK, content_type=CONTENT_TYPE)
        except ObjectDoesNotExist as e:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND, content_type=CONTENT_TYPE)
        except Exception as e:
            logger.exception(str(e))
            return HttpResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, content_type=CONTENT_TYPE)

    @has_permission("can_change_project")
    @action(methods=['POST'], url_path="execute", url_name="execute", detail=True, serializer_class=serializers.ExecuteProjectSerializer)
    def execute(self, request, pk):
        try:
            project: models.Project = models.Project.objects.get(id=pk)
            project.selected_agent_id = request.data['runner_id']
            project.status = models.Status.LAUNCHPREP
            project.save(update_fields=['selected_agent', 'status'])
            broker: MQTTClient = MQTTClient.get_instance()
            data = {'project_id':  project.id}
            project_workflow = serializers.ProjectComponentExecutionSerializer(
                data=data)
            project_workflow.is_valid(raise_exception=True)
            print(f"{project.selected_agent.agent_key}_new_project")
            broker.publish(f"{project.selected_agent.agent_key}_new_project", json.dumps({
                'project': serializers.ProjectSerializer(project).data,
                'workflow': project_workflow.data
            }))
            project_status = models.ProjectStatusLog(project=project)
            project_status.workflow = json.loads(json.dumps(project_workflow.data))
            project_status.save()
            return HttpResponse(json.dumps(serializers.ProjectStatusLogSerializer(project_status).data), status=status.HTTP_200_OK, content_type=CONTENT_TYPE)
        except Exception as e:
            logger.exception(str(e))
            return HttpResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, content_type=CONTENT_TYPE)

from app_backend import serializers, models
from rest_framework.viewsets import GenericViewSet, mixins
from rest_framework.permissions import IsAuthenticated
import logging
from rest_framework.decorators import action
from django.http import HttpResponse
from rest_framework import status
import json
from no_code_testing_app_server.utils.MqttClient import MQTTClient
logger = logging.getLogger('no_code_testing_app')
CONTENT_TYPE = "application/json"


class ProjectTestViewSet(GenericViewSet, mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin, mixins.UpdateModelMixin):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.ProjectTestCaseSerializer
    queryset = models.ProjectTestCase.objects.all()

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @action(url_name="components", detail=True, url_path="components", serializer_class=serializers.ProjectComponentSerializer, methods=['GET'])
    def test_components(self, request, pk=None):
        try:
            components = models.ProjectComponent.objects.filter(
                project_test_case__id=pk).all()
            return HttpResponse(json.dumps(serializers.ProjectComponentSerializer(components, many=True).data), status=status.HTTP_200_OK, content_type=CONTENT_TYPE)
        except Exception as e:
            logger.exception(str(e))
            return HttpResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, content_type=CONTENT_TYPE)

    @action(methods=['POST'], url_path="execute-test-case", url_name="execute-test-case", detail=True, serializer_class=serializers.ExecuteProjectSerializer)
    def execute_test_case(self, request, pk):
        try:
            test_case = models.TestFlowComponent.objects.get(id=pk)
            project: models.Project = test_case.project
            project.selected_agent_id = request.data['runner_id']
            project.status = models.Status.LAUNCHPREP
            project.save(update_fields=['selected_agent', 'status'])
            broker: MQTTClient = MQTTClient.get_instance()
            data = {"test_case_id": pk}
            project_workflow = serializers.TestCaseExecutionSerializer(
                data=data)
            project_workflow.is_valid(raise_exception=True)
            print(f"{project.selected_agent.agent_key}_new_project_test_case")
            project_status = models.ProjectStatusLog(project=project)
            # update status log type and update test flow or workflow
            execution = {
                "flows": [
                    {
                        'workflow': project_workflow.data,
                        'test_case': serializers.TestFlowComponentSerializer(test_case).data,
                    }
                ],
                "dependencies": []
            }
            project_status.workflow = json.loads(
                json.dumps(execution))
            project_status.save()
            broker.publish(f"{project.selected_agent.agent_key}_new_project_test_case", json.dumps(
                serializers.ProjectStatusLogSerializer(project_status).data))
            return HttpResponse(json.dumps(serializers.ProjectStatusLogSerializer(project_status).data), status=status.HTTP_200_OK, content_type=CONTENT_TYPE)
        except Exception as e:
            logger.exception(str(e))
            return HttpResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, content_type=CONTENT_TYPE)

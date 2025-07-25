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

    @action(methods=['POST'], url_path="execute-test-flow", url_name="execute-test-flow", detail=True, serializer_class=serializers.ExecuteProjectSerializer)
    def execute_test_flow(self, request, pk):
        try:
            flow = models.ProjectTestFlow.objects.get(id=pk)
            project: models.Project = flow.project
            project.selected_agent_id = request.data['runner_id']
            project.status = models.Status.LAUNCHPREP
            project.save(update_fields=['selected_agent', 'status'])
            broker: MQTTClient = MQTTClient.get_instance()
            data = {"test_case_id": pk}
            execution = serializers.WorkflowTestCaseExecuterSerializer(
                data={"flow_case_id": pk})
            execution.is_valid(raise_exception=True)
            project_status = models.ProjectStatusLog(project=project)
            execution.is_valid(raise_exception=True)
            project_status.workflow = json.loads(
                json.dumps(execution.data))
            project_status.save()
            broker.publish(f"{project.selected_agent.agent_key}_new_project_test_case", json.dumps(
                serializers.ProjectStatusLogSerializer(project_status).data))
            return HttpResponse(json.dumps(serializers.ProjectStatusLogSerializer(project_status).data), status=status.HTTP_200_OK, content_type=CONTENT_TYPE)
        except Exception as e:
            print(e)
            logger.exception(str(e))
            return HttpResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, content_type=CONTENT_TYPE)

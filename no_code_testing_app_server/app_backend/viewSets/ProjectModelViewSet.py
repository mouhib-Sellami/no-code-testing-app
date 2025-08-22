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
from engine_app.engines.AIEngine import AIEngine
from engine_app.models import AiGenerationJob
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
    @action(methods=['GET'], url_path="test-cases", url_name="test-cases", detail=True, serializer_class=serializers.ProjectTestCaseSerializer)
    def test_cases(self, request, pk=None, *args, **kwargs):
        try:
            tests = models.ProjectTestCase.objects.filter(
                project__id=pk, is_reference=True
            ).all()
            return HttpResponse(json.dumps(serializers.ProjectTestCaseSerializer(tests, many=True).data), status=status.HTTP_200_OK, content_type=CONTENT_TYPE)
        except ObjectDoesNotExist as e:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND, content_type=CONTENT_TYPE)
        except Exception as e:
            logger.exception(str(e))
            return HttpResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, content_type=CONTENT_TYPE)

    @has_permission("can_change_project")
    @action(methods=['GET'], url_path="test-flows", url_name="test-flows", detail=True, serializer_class=serializers.ProjectTestFlowSerializer)
    def test_flows(self, request, pk=None, *args, **kwargs):
        try:
            tests = models.ProjectTestFlow.objects.filter(
                project__id=pk).all()
            return HttpResponse(json.dumps(serializers.ProjectTestFlowSerializer(tests, many=True).data), status=status.HTTP_200_OK, content_type=CONTENT_TYPE)
        except ObjectDoesNotExist as e:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND, content_type=CONTENT_TYPE)
        except Exception as e:
            logger.exception(str(e))
            return HttpResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, content_type=CONTENT_TYPE)

    @action(methods=['POST'], url_path='ai-generate', url_name='ai-generate', detail=False)
    def ai_generate(self, request):
        try:
            print(request.data)
            test_case = models.ProjectTestCase()
            test_case.project = models.Project.objects.get(
                id=request.data['project_id'])
            test_case.name = f"AI-GENERATING..."
            test_case.save()
            job = AiGenerationJob()
            job.project = request.data['project_id']
            job.user_prompt = request.data['user_prompt']
            job.html_content = request.data['html_content']
            job.page_url = request.data['page_url']
            job.test_case = test_case.id
            job.tenant = request.tenant
            job.save()
            ai_engine: AIEngine = AIEngine.get_instance()
            ai_engine.add_task(job=job, delete_when_finish=False)
            return HttpResponse(status=status.HTTP_201_CREATED, content_type=CONTENT_TYPE)
        except Exception as e:
            print(e)
            logger.exception(str(e))
            return HttpResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, content_type=CONTENT_TYPE)

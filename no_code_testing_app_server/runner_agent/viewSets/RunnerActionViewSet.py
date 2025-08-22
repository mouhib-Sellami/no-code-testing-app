import json
import logging
from runner_agent import models, serializers
from rest_framework.viewsets import GenericViewSet, mixins
from rest_framework.decorators import action
from rest_framework import status
from django.http import HttpResponse
from app_backend import models as BACK_MODELS
from no_code_testing_app_server.minio_bucket.MinioClient import MinioClient

logger = logging.getLogger('no_code_testing_app')
CONTENT_TYPE = 'application/json'


class RunnerActionViewSet(GenericViewSet, mixins.UpdateModelMixin):

    serializer_class = serializers.RunnerAgentSerializer
    queryset = models.RunnerAgent.objects.all().order_by('created_at')

    def __init__(self, **kwargs):
        self.minio: MinioClient = MinioClient.get_instance()
        super().__init__(**kwargs)

    @action(url_path="", url_name="", methods=['POST'], serializer_class=serializers.RunnerAgentSerializer, detail=False)
    def register(self, request):
        try:
            runner_agent: models.RunnerAgent = request.runner_agent
            update_fields = ['status']
            for key, value in request.data.items():
                setattr(runner_agent, key, value)
                update_fields.append(key)
            runner_agent.status = models.RunnerAgentStatus.INITIALIZING
            runner_agent.save(update_fields=update_fields)
            result = serializers.RunnerAgentSerializer(runner_agent).data
            result.update({'tenant_id': request.tenant.id})
            return HttpResponse(json.dumps(result), status=status.HTTP_200_OK, content_type=CONTENT_TYPE)
        except Exception as e:
            print(e)
            return HttpResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, content_type=CONTENT_TYPE)

    @action(url_path="update-execution-status", url_name="update-execution-status", methods=['PUT'], detail=False)
    def update_execution_status(self, request):
        try:
            execution = BACK_MODELS.ProjectStatusLog.objects.get(
                id=request.data['execution_id'])
            project = execution.project
            execution.old_status = execution.new_status
            execution.is_failed = BACK_MODELS.Status.CRASHLANDING.value == request.data[
                'status']
            execution.is_running = BACK_MODELS.Status.GALACTICCRUISE.value == request.data[
                'status']
            execution.is_finish = BACK_MODELS.Status.STELLARFINALE.value == request.data[
                'status']
            execution.new_status = request.data['status']
            execution.save(update_fields=[
                           'old_status', 'new_status', 'is_failed', 'is_running', 'is_finish'])
            project.status = request.data['status']
            project.save(update_fields=['status'])
            if request.data.get("new_payload") != None:
                execution.workflow = json.loads(
                    request.data.get("new_payload"))
                execution.save(update_fields=['workflow'])
            return HttpResponse(json.dumps({'status': 'ok'}), status=status.HTTP_200_OK, content_type=CONTENT_TYPE)
        except Exception as e:
            logger.exception(str(e))
            return HttpResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, content_type=CONTENT_TYPE)

    @action(url_path="upload-test-case-image", url_name="upload-test-case-image", methods=['POST'], detail=False)
    def upload_test_case_image(self, request):
        try:
            folder_name = request.data['execution_id']
            self.minio.create_folder(folder_name)
            file_name = ""
            for count, x in enumerate(request.FILES.getlist("files")):
                filename = self.minio.upload_single(x, folder_name)
            file_link = self.minio.get_public_link(folder_name + "/" + filename)
            return HttpResponse(json.dumps({"public_link": file_link}), status=status.HTTP_200_OK, content_type=CONTENT_TYPE)
        except Exception as e:
            logger.exception(str(e))
            print(e)
            return HttpResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, content_type=CONTENT_TYPE)

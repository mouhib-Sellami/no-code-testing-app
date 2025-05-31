import json
import logging
from runner_agent import models, serializers
from rest_framework.viewsets import GenericViewSet, mixins
from rest_framework.decorators import action
from rest_framework import status
from django.http import HttpResponse

logger = logging.getLogger('no_code_testing_app')
CONTENT_TYPE = 'application/json'


class RunnerActionViewSet(GenericViewSet, mixins.UpdateModelMixin):

    serializer_class = serializers.RunnerAgentSerializer
    queryset = models.RunnerAgent.objects.all().order_by('created_at')

    @action(url_path="", url_name="", methods=['POST'], serializer_class=serializers.RunnerAgentSerializer, detail=False)
    def register(self, request):
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

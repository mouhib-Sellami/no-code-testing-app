import logging
from runner_agent import models, serializers
from app_user_auth.auth_decorators.decorators import has_permission
from no_code_testing_app_server.shared import BaseModelViewSet

logger = logging.getLogger('no_code_testing_app')
CONTENT_TYPE = 'application/json'


class RunnerModelViewSet(BaseModelViewSet):

    serializer_class = serializers.RunnerAgentSerializer
    queryset = models.RunnerAgent.objects.all().order_by('created_at')

    @has_permission("can_view_all_runner_agent")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @has_permission("can_create_runner_agent")
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @has_permission("can_change_runner_agent")
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @has_permission("can_delete_runner_agent")
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @has_permission("can_view_runner_agent")
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @has_permission("can_change_runner_agent")
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

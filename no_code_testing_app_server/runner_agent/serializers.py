from no_code_testing_app_server.shared import DynamicModelSerializer
from runner_agent import models


class RunnerAgentSerializer(DynamicModelSerializer):

    class Meta:
        model = models.RunnerAgent
        fields = '__all__'

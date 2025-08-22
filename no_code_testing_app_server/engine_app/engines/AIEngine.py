from no_code_testing_app_server.patterns import singleton
from engine.core.Engine import Engine
from engine.conf import TASK_TYPE


@singleton
class AIEngine(Engine):
    def __init__(self):
        super().__init__(task_type=TASK_TYPE.ai)

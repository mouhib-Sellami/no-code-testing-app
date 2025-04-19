
from engine.core.Exceptions import TaskMissingWorkerClass
from django.conf import settings
from enum import Enum
import logging
logger = logging.getLogger('Engine')


class BaseEnum(Enum):
    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))


TASK_TYPE = BaseEnum('TASK_TYPES', settings.TASK_TYPES)

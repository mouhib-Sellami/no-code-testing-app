from django.conf import settings
from engine.core.Exceptions import TaskMissingWorkerClass
import logging
logger = logging.getLogger('Engine')

def get_engine_worker(task_type):
    if settings.TASK_WORKER_CLASS.get(task_type):
        module_decompose = settings.TASK_WORKER_CLASS[task_type].split(
            '.')
        module = __import__(
            '.'.join(module_decompose[:-1]), fromlist=[module_decompose[-1]])
        WORKER_CLASS = getattr(module, module_decompose[-1])
        return WORKER_CLASS
    else:
        raise TaskMissingWorkerClass(
            f"{task_type} has no worker class")

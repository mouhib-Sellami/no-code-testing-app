import queue
from typing import Any
from engine.models import Task
import logging
logger = logging.getLogger('Engine')


class EngineQueue(queue.Queue):
    def __init__(self, maxsize: int = 0) -> None:
        super().__init__(maxsize)

    def task_finish(self, task: Task) -> None:
        try:
            if task.delete_when_finish:
                task.job_payload.delete()
                task.delete()
        except Exception as e:
            logger.exception(e)
        return super().task_done()

    def rejoin_element(self, element: Any):
        self.queue.appendleft(element)

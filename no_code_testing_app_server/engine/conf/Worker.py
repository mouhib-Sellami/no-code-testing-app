from abc import ABC, abstractmethod
from engine.models import Task, Status, FailedTask
from engine.core.Exceptions import EngineMissingArgs
from engine.core.EngineQueue import EngineQueue
from engine.core.EngineQueue import EngineQueue
from uuid import uuid4
import logging
import time
import datetime
import traceback
logger = logging.getLogger('Engine')


class Worker(ABC):
    task: Task = None
    queue: EngineQueue = None
    worker_id = uuid4()
    worker_name = "Worker - "

    @classmethod
    def get_worker(cls, **kwargs):
        return cls(**kwargs)

    def __init__(self, **kwargs) -> None:
        for key, value in kwargs.items():
            setattr(self, key, value)

    @abstractmethod
    def worker_runner(self, task: Task):
        '''
        params : 
            task : 
            kwargs : {}
            description : super().worker_runner() // add custom custom runner
            to access the task use self.task
        '''
        self.task.executed_at = datetime.datetime.now()
        self.task.status = Status.running
        self._update_task(['executed_at', 'status'])

    def _check_update_attempts(self):
        """"""
        if self.task.attempts < self.task.max_attempts:
            self.task.attempts += 1
            self._update_task(['attempts'])
            return True
        return False

    def _when_exception(self, exception: Exception):
        logger.exception(exception)
        check_attempts = self._check_update_attempts()
        if check_attempts:
            self.queue.rejoin_element(self)
            self.on_exception_callback(task=self.task, exception=exception)
        else:
            failed_task = FailedTask()
            failed_task.task = self.task
            failed_task.exception = str(traceback.format_exc())
            failed_task.exception_name = exception.__class__.__name__
            failed_task.failed_on = datetime.datetime.now()
            failed_task.save()
            self.task.is_done = False
            self.task.status = Status.failed
            self.task.finished_at = datetime.datetime.now()
            self._update_task(['is_done', 'status', 'finished_at'])
            self.queue.task_finish(self.task)
            self.on_failed_callback(
                failed_task=failed_task, exception=exception)

    def _when_finish(self):
        self.task.finished_at = datetime.datetime.now()
        self.task.execution_time = self.task.finished_at-self.task.executed_at
        self.task.is_done = True
        self.task.status = Status.finish
        self._update_task(
            ['finished_at', 'execution_time', 'status', 'is_done'])
        self.on_finish_callback(task=self.task)

    @abstractmethod
    def on_finish_callback(self, task: Task):
        '''update when worker is finish  '''
        pass

    @abstractmethod
    def on_failed_callback(self, failed_task: FailedTask, exception: Exception):
        '''update when worker have failed  '''
        logger.exception(exception)

    @abstractmethod
    def on_exception_callback(self, task: Task, exception: Exception):
        '''update when worker have exception  '''
        logger.exception(exception)

    def run_worker(self):
        try:
            start = time.time()
            logging.info(f"starting {self.worker_name} - {self.worker_id}")
            self.worker_runner(self.task)
            self._when_finish()
            logger.info(
                f"{self.worker_name} - {self.worker_id} finish in {time.time()-start}")
            return True
        except Exception as e:
            logger.exception(str(e))
            self._when_exception(exception=e)
            return False

    def _update_task(self, update_fields=[]):
        self.task.save(update_fields=update_fields)

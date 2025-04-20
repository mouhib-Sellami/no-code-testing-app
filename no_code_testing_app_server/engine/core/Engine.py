from .EngineQueue import EngineQueue
from .Exceptions import EngineMissingTaskTypes
from engine.models import Task, JobBaseModal, Status
from django.db.models import F
from engine.conf.Worker import Worker
from uuid import uuid4
import threading
import logging
import time
from engine.conf import TASK_TYPE
from engine.conf import get_engine_worker
logger = logging.getLogger('Engine')


class Engine():
    task_model: Task = Task
    engine_name = "Engine - "
    engine_id = uuid4()

    def __init__(self, task_type=None, delay_empty: int = 3, engine_name: str = "Engine - ", **kwargs) -> None:
        f'''params : 
                delay: in second (delay if the queue is empty) default 3 seconds
                engine_type : TASK_TYPES : {TASK_TYPE.list()} required
                engine_name : default Engine -
                '''
        for key, value in kwargs.items():
            setattr(self, key, value)
        if task_type == None:
            raise EngineMissingTaskTypes(
                "Engine missing task type, specify task type in the __init__ function ")
        self.task_type = task_type
        self.worker_class: Worker = get_engine_worker(self.task_type.name)
        self.delay_empty = delay_empty
        self.queue = EngineQueue()
        self.start_time = time.time()
        self.running_task: Task = None
        self.engine_name = engine_name
        self.load_tasks()
        self._run_engine()

    def load_tasks(self):
        self.queue = EngineQueue()
        [self.queue.put(self.worker_class.get_worker(task=task, queue=self.queue))
         for task in list(self.task_model.objects.filter(task_type=self.task_type.name, is_done=False, status=Status.pending, attempts__lte=F('max_attempts')).order_by('created_at').all())]

    def add_task(self, job: JobBaseModal = None, task: Task = None, new: bool = True, delete_when_finish=True):
        if new and task != None:
            self.queue.put(self.worker_class.get_worker(
                task=self.task_model.objects.create(job_payload=task.job_payload, task_type=self.task_type.name, delete_when_finish=delete_when_finish), queue=self.queue))
            return
        if new and task == None:
            self.queue.put(self.worker_class.get_worker(
                task=self.task_model.objects.create(job_payload=job, task_type=self.task_type.name, delete_when_finish=delete_when_finish), queue=self.queue))
        else:
            task.task_type = self.task_type.name
            task.is_done = False
            task.status = Status.pending
            task.delete_when_finish = delete_when_finish
            task.save(update_fields=['task_type', 'is_done', 'status'])
            self.queue.put(self.worker_class.get_worker(
                task=task, queue=self.queue))

    def _run_engine(self):
        logger.info(f"{self.engine_name} - {str(self.engine_id)} is starting")
        self.queue_thread = threading.Thread(target=self._execute_queue)
        self.queue_thread.daemon = True
        self.queue_thread.start()
        logger.info(f"{self.engine_name} - {str(self.engine_id)} is running")
        return True

    def stop_engine(self):
        logger.info(f"{self.engine_name} - {str(self.engine_id)} is stopping")
        self.queue.join()
        self.queue_thread.join()
        logger.info(f"{self.engine_name} - {str(self.engine_id)} is stop")

    def get_running_task(self):
        return self.running_task

    def _execute_queue(self):
        while True:
            if self.queue.empty():
                time.sleep(self.delay_empty)
            else:
                worker: Worker = self.queue.get()
                self.running_task = worker.task
                process_check = worker.run_worker()
                if process_check:
                    self.queue.task_finish(task=worker.task)

# Django task engine

Copy engine app into aa django project

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install foobar.

```bash
pip install -r engine/requirements.txt
```

## settings.py

```python

# Application definition

INSTALLED_APPS = [
    ...
    'engine',
    ...
]

#add task type of engine types
TASK_TYPES = {"process": "Process"}

#add task class workers for auto mapping jobs base on task type
TASK_WORKER_CLASS = {
    'edit': 'app.workers.ExampleWorker.ExampleWorker',
}
```

## Worker Class
```python
from engine.conf.Worker import Worker
from engine.models import FailedTask, Task


class EditWorker(Worker):

    def on_exception_callback(self, task: Task, exception: Exception):
        super().on_exception_callback(task, exception)

    def on_failed_callback(self, failed_task: FailedTask, exception: Exception):
        super().on_failed_callback(failed_task, exception)

    def on_finish_callback(self, task: Task):
        super().on_finish_callback(task)

    def worker_runner(self, task: Task):
        super().worker_runner(task)


```

## Init engine

```python
from engine.core.Engine import Engine
from engine.conf import TASK_TYPE

engine = Engine(task_type=TASK_TYPE.edit)

```
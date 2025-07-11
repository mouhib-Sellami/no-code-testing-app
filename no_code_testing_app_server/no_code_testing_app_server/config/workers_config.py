
TASK_TYPES = {
    'mail': 'mail'
}

TASK_WORKER_CLASS = {
    'mail': 'engine_app.engine_workers.EmailWorker.EmailWorker'
}
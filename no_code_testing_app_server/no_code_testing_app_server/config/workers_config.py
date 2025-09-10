
TASK_TYPES = {
    'mail': 'mail',
    'ai': 'ai',
    'audit': 'audit',
}

TASK_WORKER_CLASS = {
    'mail': 'engine_app.engine_workers.EmailWorker.EmailWorker',
    'ai': 'engine_app.engine_workers.AiGenerationWorker.AiGenerationWorker',
    'audit': 'engine_app.engine_workers.AiAuditGenerationWorker.AiAuditGenerationWorker',
}
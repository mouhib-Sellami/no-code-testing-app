from engine.conf.Worker import Worker
from engine.models import FailedTask, Task
from no_code_testing_app_server.utils.ai.WebAudit import WebAudit
from engine_app import models as ENGINE_MODELS
from engine_app.engines.MailingEngine import MailingEngine


class AiAuditGenerationWorker(Worker):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.audit_generator: WebAudit = WebAudit.get_instance()
        self.mail_engine: MailingEngine = MailingEngine.get_instance()

    def on_exception_callback(self, task: Task, exception: Exception):
        super().on_exception_callback(task, exception)

    def on_failed_callback(self, failed_task: FailedTask, exception: Exception):
        super().on_failed_callback(failed_task, exception)

    def on_finish_callback(self, task: Task):
        super().on_finish_callback(task)

    def worker_runner(self, task: Task):
        super().worker_runner(task)
        job: ENGINE_MODELS.AiAuditJob = task.job_payload
        audit_html = self.audit_generator.run(
            html_content=job.html_content)
        print("audit_html")
        print(audit_html)
        email_job = ENGINE_MODELS.MailJobs()
        email_job.type = ENGINE_MODELS.MailJobs.EmailTypes.AUDIT
        email_job.receiver = job.user
        email_job.email_content = audit_html
        email_job.save()
        self.mail_engine.add_task(job=email_job, delete_when_finish=False,new=True)

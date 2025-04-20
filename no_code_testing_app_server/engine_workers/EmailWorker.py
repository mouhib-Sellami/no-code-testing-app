from app_user_auth import models
from engine.conf.Worker import Worker
from engine.models import FailedTask, Task
from app_user_auth.viewSets import serializers
from no_code_testing_app_server.config.mail_jet_config import MailJet
from no_code_testing_app_server.config.mailing.mailing import generate_email


class EmailWorker(Worker):
    def on_exception_callback(self, task: Task, exception: Exception):
        super().on_exception_callback(task, exception)

    def on_failed_callback(self, failed_task: FailedTask, exception: Exception):
        super().on_failed_callback(failed_task, exception)

    def on_finish_callback(self, task: Task):
        super().on_finish_callback(task)

    def worker_runner(self, task: Task):
        super().worker_runner(task)
        mail_jet_client: MailJet = MailJet.get_instance()
        job_payload: models.MailJobs = task.job_payload
        user_parsed = serializers.BaseUserSerializer(
            job_payload.receiver, context={'extra_fields': ['reset_token']}).data
        email_to_send = generate_email(
            receiver=user_parsed['email'], type=job_payload.type, **user_parsed)

        mail_jet_client.send_email(email_to_send)
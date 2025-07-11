from app_user_auth import models
from engine_app import models as appEngineModels
from engine_app.views import mailing_engine
from no_code_testing_app_server.utils import create_tiny_token


def handle_reset_password_request(user: models.TenantUser):
    user.reset_token = create_tiny_token()
    user.save(update_fields=['reset_token'])
    job = appEngineModels.MailJobs.objects.create(
        receiver=user, type=appEngineModels.MailJobs.EmailTypes.RESET_PASSWORD)
    mailing_engine.add_task(
        job=job, delete_when_finish=False, new=True)


def handle_new_user_creation(user: models.TenantUser):
    user.reset_token = create_tiny_token()
    user.is_active = False
    user.save(update_fields=['reset_token', 'is_active'])
    job = appEngineModels.MailJobs.objects.create(
        receiver=user, type=appEngineModels.MailJobs.EmailTypes.NEW_USER)
    mailing_engine.add_task(
        job=job, delete_when_finish=False, new=True)

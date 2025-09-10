from django.db import models
from engine import models as engineModels
from app_tenant import models as TENANT_MODELS
from app_user_auth import models as AUTH_MODELS
# Create your models here.

from django.conf import settings


class MailJobs(engineModels.JobBaseModal):
    class EmailTypes(models.TextChoices):
        RESET_PASSWORD = 'RESET_PASSWORD'
        REQUEST_NEW_PASSWORD = 'REQUEST_NEW_PASSWORD'
        NEW_USER = 'NEW_USER'
        NEW_ORG = 'NEW_ORG'
        AUDIT = 'AUDIT'

    class Meta:
        app_label = 'engine_app'
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="engine_app_mailjobs")
    type = models.CharField(choices=EmailTypes.choices, max_length=255)
    email_content = models.TextField(default=None, null=True)


class AiGenerationJob(engineModels.JobBaseModal):
    class Meta:
        app_label = 'engine_app'

    project = models.CharField(
        max_length=255, null=False, blank=True, default="0")
    test_case = models.CharField(
        max_length=255, null=False, blank=True, default="0")
    tenant = models.ForeignKey(
        TENANT_MODELS.Tenant, on_delete=models.CASCADE, default=None)
    html_content = models.TextField(blank=True)
    user_prompt = models.TextField()
    page_url = models.TextField(blank=False, null=True, default=None)


class AiAuditJob(engineModels.JobBaseModal):
    class Meta:
        app_label = 'engine_app'

    html_content = models.TextField(blank=True)
    user = models.ForeignKey(AUTH_MODELS.TenantUser, on_delete=models.CASCADE)

from django.db import models
from engine import models as engineModels
# Create your models here.

from django.conf import settings


class MailJobs(engineModels.JobBaseModal):
    class EmailTypes(models.TextChoices):
        RESET_PASSWORD = 'RESET_PASSWORD'
        REQUEST_NEW_PASSWORD = 'REQUEST_NEW_PASSWORD'
        NEW_USER = 'NEW_USER'
        NEW_ORG = 'NEW_ORG'

    class Meta:
        app_label = 'engine_app'
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="engine_app_mailjobs")
    type = models.CharField(choices=EmailTypes.choices, max_length=255)

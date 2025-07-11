from django.db import models
from no_code_testing_app_server.shared.BaseModel import BaseModel
from django.utils import timezone
from no_code_testing_app_server.utils.utils import create_tiny_token
from uuid import uuid4
from secrets import token_urlsafe


class RunnerAgentStatus(models.TextChoices):
    RUNNING = 'Running'
    INACTIVE = 'Inactive'
    ACTIVE = 'Active'
    ERROR = 'Error'
    INITIALIZING = 'Initializing'
    READY = 'Ready to run'


class RunnerAgentEnvironment(models.TextChoices):
    LOCAL = 'Local'
    CLOUD = 'Cloud'
    DOCKER = 'Docker'


class RunnerAgentTaskType(models.TextChoices):
    WEB = 'Web'


class RunnerAgent(BaseModel):
    agent_key = models.UUIDField(
        default=uuid4,
        editable=False, unique=True, auto_created=True)
    name = models.CharField(max_length=255)

    last_heartbeat = models.DateTimeField(
        null=True,
        blank=True,
    )

    auth_token = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        unique=True,
        editable=False
    )

    description = models.TextField(blank=True, null=True)
    host_machine_name = models.CharField(max_length=255, null=True, blank=True)
    host_machine_ip = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=RunnerAgentStatus.choices,
        default=RunnerAgentStatus.INACTIVE,
    )
    environment = models.CharField(
        max_length=20,
        choices=RunnerAgentEnvironment.choices,
        default=RunnerAgentEnvironment.LOCAL,
    )

    def update_heartbeat(self):
        self.last_heartbeat = timezone.now()
        self.save()

    def generate_auth_token(self):
        self.auth_token = token_urlsafe(24)
        return self.auth_token

    def save(self, *args, **kwargs):
        if not self.auth_token:
            self.auth_token = self.generate_auth_token()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

from django.db import models
from django.utils.translation import gettext_lazy as _
from polymorphic.models import PolymorphicModel
import uuid
from engine.conf import TASK_TYPE
# Create your models here.


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def attributes(self):
        return self.__dict__

    class Meta:
        abstract = True


class Status(models.TextChoices):
    running = "running", _('Running')
    pending = "pending", _('Pending')
    failed = "failed", _('Failed')
    finish = "finish", _('Finish')


class JobBaseModal(PolymorphicModel, BaseModel):
    uuid = models.UUIDField(auto_created=True, default=uuid.uuid4, null=True,editable=False)

    def __str__(self) -> str:
        return str(self.uuid)


class Task(BaseModel):
    uuid = models.UUIDField(auto_created=True, default=uuid.uuid4, null=True,editable=False)
    attempts = models.IntegerField(default=0)
    max_attempts = models.IntegerField(default=3)
    executed_at = models.DateTimeField(null=True, blank=True, default=None)
    finished_at = models.DateTimeField(null=True, blank=True)
    execution_time = models.DurationField(null=True, blank=True, default=None)
    is_done = models.BooleanField(default=False)
    delete_when_finish = models.BooleanField(default=True)
    job_payload = models.ForeignKey(
        JobBaseModal, related_name="job_task", on_delete=models.CASCADE)
    task_type = models.CharField(
        choices=[(tag.name, tag.value) for tag in TASK_TYPE],
        max_length=255,
        null=True, blank=True
    )
    status = models.CharField(
        choices=Status.choices,
        default=Status.pending,
        max_length=255,
        null=True, blank=True
    )
    
    def __str__(self) -> str:
        return str(self.uuid) + " | " + self.job_payload.__str__()


class FailedTask(BaseModel):
    task = models.ForeignKey(
        Task, related_name="task_failed", on_delete=models.CASCADE, null=True, default=None)
    exception_name = models.CharField(max_length=255, null=True, blank=True)
    exception = models.TextField(blank=True, null=True)
    failed_on = models.DateTimeField(auto_now_add=True, null=True)

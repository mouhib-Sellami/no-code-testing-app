import os
from uuid import uuid4
from django.db import models
from django.conf import settings
from no_code_testing_app_server.shared import BaseModel
from no_code_testing_app_server.utils.modelValidate import validate_image_extension
from runner_agent import models as AGENT_MODELS
# add provider type for engine worker selection


class Kwarg(BaseModel):
    label = models.CharField(max_length=255, null=False, blank=False)
    value = models.CharField(max_length=255, null=True, blank=True, default="")

    def __str__(self):
        return self.label if self.value is None else self.label + " - " + self.value


class ComponentType(models.TextChoices):
    INPUT = 'input', 'Input'
    OUTPUT = 'output', 'Output'
    INNOUT = 'input-output', 'input-output'


class Component(BaseModel):
    name = models.CharField(max_length=255, null=False, blank=False)
    action_name = models.CharField(max_length=255, null=False, blank=False)
    module = models.CharField(max_length=255, null=True, blank=True)
    initial_config = models.JSONField(null=True, blank=True)
    extra_download_assets = models.TextField(blank=True, null=True)
    is_function = models.BooleanField(default=False)
    is_default = models.BooleanField(default=False)
    extra_arguments = models.ManyToManyField(
        Kwarg, related_name="extra_arguments_kwargs", blank=True)
    default_arguments = models.ManyToManyField(
        Kwarg, related_name="default_arguments_kwargs", blank=True)
    type = models.CharField(
        max_length=50,
        choices=ComponentType.choices,
        default=ComponentType.INPUT,
        null=False,
        blank=False
    )

    def __str__(self):
        return self.name + " - " + self.action_name


class Dependency(BaseModel):
    name = models.CharField(max_length=255, null=False, blank=False)
    version = models.CharField(max_length=255, null=False, blank=False)

    def __str__(self):
        return self.name + " - " + self.version


class Category(BaseModel):
    name = models.CharField(max_length=255, null=False, blank=False)
    components = models.ManyToManyField(
        Component, related_name="component_providers", blank=True)

    def __str__(self):
        return self.name


class Provider(BaseModel):
    def generate_upload_path(self, filename):
        upload_folder = os.path.join(
            settings.MEDIA_ROOT, self.name)
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        return os.path.join(upload_folder, f'{uuid4()}-{filename}')

    name = models.CharField(max_length=255, null=False, blank=False)
    version = models.CharField(max_length=255, null=False, blank=False)
    image = models.FileField(upload_to=generate_upload_path, default=None, null=True, blank=True, validators=[
        validate_image_extension], max_length=500)
    initial_config = models.JSONField(null=True, blank=True)
    extra_download_assets = models.TextField(blank=True, null=True)
    categories = models.ManyToManyField(
        Category, blank=False, related_name="category_providers")
    dependencies = models.ManyToManyField(
        Dependency, related_name="dependency_providers", blank=True)
    is_active = models.BooleanField(default=False)
    provider_type = models.CharField(
        max_length=20,
        choices=AGENT_MODELS.RunnerAgentTaskType.choices,
        default=AGENT_MODELS.RunnerAgentTaskType.WEB,
    )

    def __str__(self):
        return self.name + " - " + self.version

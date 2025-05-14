import os
from uuid import uuid4
from django.db import models
from django.conf import settings
from no_code_testing_app_server.shared import BaseModel
from no_code_testing_app_server.utils.modelValidate import validate_image_extension

# add provider type for engine worker selection


class Kwarg(BaseModel):
    label = models.CharField(max_length=255, null=False, blank=False)
    value = models.CharField(max_length=255, null=True, blank=True, default="")

    def __str__(self):
        return self.label if self.value is None else self.label + " - " + self.value


class Component(BaseModel):
    name = models.CharField(max_length=255, null=False, blank=False)
    action_name = models.CharField(max_length=255, null=False, blank=False)
    module = models.CharField(max_length=255, null=True, blank=True)
    initial_config = models.JSONField(null=True, blank=True)
    extra_download_assets = models.TextField(blank=True, null=True)
    is_function = models.BooleanField(default=False)
    extra_arguments = models.ManyToManyField(
        Kwarg, related_name="extra_arguments_kwargs", null=True, blank=True)
    default_arguments = models.ManyToManyField(
        Kwarg, related_name="default_arguments_kwargs", null=True, blank=True)

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
        Component, related_name="component_providers", null=True, blank=True)

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
        Category, null=True, blank=False, related_name="category_providers")
    dependencies = models.ManyToManyField(
        Dependency, related_name="dependency_providers", null=True, blank=True)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.name + " - " + self.version

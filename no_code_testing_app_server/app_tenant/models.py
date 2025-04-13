from django.db import models
from tenant_users.tenants.models import TenantBase
from django.conf import settings
import os
from uuid import uuid4
from no_code_testing_app_server.utils.BaseModel import BaseModel
from no_code_testing_app_server.utils.modelValidate import validate_image_extension


class Tenant(TenantBase, BaseModel):
    def generate_upload_path(self, filename):
        upload_folder = os.path.join(
            settings.STATICFILES_DIRS[0], self.name)
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        return os.path.join(upload_folder, f'{uuid4()}-{filename}')
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True
    )
    auto_create_schema = True
    name = models.CharField(max_length=255, null=False,
                            unique=True, blank=False, editable=False)
    email = models.CharField(max_length=255, null=True,
                             blank=True, unique=True, default="")
    org_pic = models.FileField(upload_to=generate_upload_path, default=None, null=True, blank=True, validators=[
        validate_image_extension], max_length=500)

    def __str__(self):
        return self.name


class Domain(BaseModel):
    domain = models.CharField(max_length=100)
    tenant = models.ForeignKey(
        Tenant, on_delete=models.CASCADE, related_name="domain_set")
    is_primary = models.BooleanField(default=True)

    def __str__(self):
        return self.domain

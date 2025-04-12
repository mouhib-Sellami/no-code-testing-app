from django.db import models
from no_code_testing_app_server.utils.BaseModel import BaseModel
from no_code_testing_app_server.utils.modelValidate import validate_image_extension
from app_user_auth import models as authModels
from app_tenant import models as tenantModels


class Project(BaseModel):
    name = models.CharField(max_length=255)


class AppPermission(BaseModel):
    label = models.CharField(max_length=255, null=False,
                             blank=True, default="", unique=True)

    def __str__(self) -> str:
        return self.label


class OrgRole(BaseModel):
    name = models.CharField(max_length=255, default='', null=True, blank=True)
    slug = models.CharField(max_length=255, default='', null=True, blank=True)
    permissions = models.ManyToManyField(
        AppPermission, related_name='role_permission')
    active = models.BooleanField(default=True)
    can_delete = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.name


class User(BaseModel):
    user = models.OneToOneField(
        authModels.TenantUser, on_delete=models.DO_NOTHING, related_name='app_user', null=True)
    first_name = models.CharField(max_length=255, null=True, blank=False)
    last_name = models.CharField(max_length=255, null=True, blank=False)
    profession = models.CharField(max_length=255, null=True, blank=False)
    role = models.ForeignKey(
        OrgRole, on_delete=models.CASCADE, related_name="role_org_member")

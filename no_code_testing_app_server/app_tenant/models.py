from django.db import models
from tenant_users.tenants.models import TenantBase
from utils.BaseModel import BaseModel


class Tenant(TenantBase, BaseModel):
    name = models.CharField(max_length=100)
    auto_create_schema = True

    def __str__(self):
        return self.name


class Domain(BaseModel):
    domain = models.CharField(max_length=100)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE,related_name="domain_set")
    is_primary = models.BooleanField(default=True)

    def __str__(self):
        return self.domain

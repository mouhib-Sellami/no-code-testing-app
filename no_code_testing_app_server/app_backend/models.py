from django.db import models
from no_code_testing_app_server.utils.BaseModel import BaseModel
from app_user_auth import models as authModels
class Project(BaseModel):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(authModels.TenantUser,on_delete=models.CASCADE,related_name='user_projects',null=True)

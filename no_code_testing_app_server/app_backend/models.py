from django.db import models
from no_code_testing_app_server.utils.BaseModel import BaseModel

class Project(BaseModel):
    name = models.CharField(max_length=255)

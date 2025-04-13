from django.db import models
from utils.BaseModel import BaseModel
# Create your models here.

class Project(BaseModel):
    name = models.CharField(max_length=255)

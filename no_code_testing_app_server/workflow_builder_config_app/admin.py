from django.contrib import admin
from . import models
# Register your models here.
admin.site.register(models.Provider)
admin.site.register(models.Component)
admin.site.register(models.Dependency)
admin.site.register(models.Kwarg)
admin.site.register(models.Category)

from django.contrib import admin
from . import models
# Register your models here.

admin.site.register(models.Project)
admin.site.register(models.User)
admin.site.register(models.OrgRole)
admin.site.register(models.AppPermission)
admin.site.register(models.ProjectComponent)
admin.site.register(models.ProjectStatusLog)
admin.site.register(models.Kwarg)
admin.site.register(models.ComponentDependency)
admin.site.register(models.ProjectTestFlow)
admin.site.register(models.ProjectTestCase)
admin.site.register(models.ProjectTestFlowAtomicCases)
admin.site.register(models.TestFlowComponent)
admin.site.register(models.TestFlowDependency)
# admin.site.register(models.TestCase)

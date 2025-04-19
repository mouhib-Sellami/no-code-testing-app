from django.contrib import admin
from django.contrib import messages
from . import models
from engine.core.Engine import Engine

import gc
from engine.conf import TASK_TYPE


def get_engine_instance(engine_type) -> Engine | None:
    for obj in gc.get_objects():
        if isinstance(obj, Engine) and obj.task_type.name == engine_type:
            return obj
    return None


# Register your models here.
list_page = 20


@admin.action(description='Restart Task')
def restart_task(modeladmin, request, queryset):
    for task in queryset:
        task.is_done = False
        task.status = models.Status.pending
        task.attempts = 0
        task.save(update_fields=['is_done', 'status', 'attempts'])
        engine = get_engine_instance(task.task_type)
        if engine:
            engine.load_tasks()
    messages.add_message(request, messages.INFO, "engine loaded queues")

class TaskAdmin(admin.ModelAdmin):
    list_display = ['id', 'job_payload', 'task_type',
                    'status', 'created_at', 'updated_at']
    ordering = ['is_done', 'created_at']
    actions = [restart_task]
    list_filter = ('task_type','status')

    list_per_page = list_page


class FailedTaskAdmin(admin.ModelAdmin):
    list_display = ['id', 'task', 'exception_name', 'exception',
                    'created_at', 'updated_at']
    list_per_page = list_page


admin.site.register(models.Task, TaskAdmin)
admin.site.register(models.FailedTask,FailedTaskAdmin)

from django.apps import AppConfig


class EngineConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'engine'
    Worker_implementation = None

    def ready(self) -> None:
        from django.conf import settings
        from engine.core.Exceptions import TaskMissingWorkerClass, EngineMissingTaskTypes
        self.Worker_implementation = None

        if not hasattr(settings, 'TASK_WORKER_CLASS'):
            raise TaskMissingWorkerClass(
                "add TASK_WORKER_CLASS {'task_type':'classPath'...} to settings.py and specify the path to the worker overridden class ")
        if not hasattr(settings, "TASK_TYPES"):
            raise EngineMissingTaskTypes(
                "define TASK_TYPES in settings.py as {example : 'Example' ...} key used as type , value used to display")
        return super().ready()

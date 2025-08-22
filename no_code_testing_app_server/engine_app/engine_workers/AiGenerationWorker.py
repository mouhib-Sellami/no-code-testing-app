from engine.conf.Worker import Worker
from engine.models import FailedTask, Task
from no_code_testing_app_server.utils.ai.TestCaseGenerator import TestCaseGenerator
from engine_app import models as ENGINE_MODELS
from django_tenants.utils import tenant_context
from app_backend import models as APP_MODELS
from workflow_builder_config_app import models as PROVIDER_MODELS
from app_backend import serializers


class AiGenerationWorker(Worker):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.test_case_generator: TestCaseGenerator = TestCaseGenerator.get_instance()

    def on_exception_callback(self, task: Task, exception: Exception):
        super().on_exception_callback(task, exception)

    def on_failed_callback(self, failed_task: FailedTask, exception: Exception):
        super().on_failed_callback(failed_task, exception)

    def on_finish_callback(self, task: Task):
        super().on_finish_callback(task)

    def worker_runner(self, task: Task):
        super().worker_runner(task)
        job: ENGINE_MODELS.AiGenerationJob = task.job_payload
        test_case_gen = self.test_case_generator.run(
            user_prompt=job.user_prompt, html_content=job.html_content, page_url=job.page_url)
        print("="*100)
        print(test_case_gen)
        print("="*100)
        with tenant_context(job.tenant):
            test_case = APP_MODELS.ProjectTestCase.objects.get(
                id=int(job.test_case))
            APP_MODELS.ProjectComponent.objects.filter(
                project_test_case=test_case).all().delete()
            if test_case_gen.get("test_case_name"):
                test_case.name = test_case_gen.get("test_case_name")
                test_case.save(update_fields=["name"])

            comps = test_case_gen.get("components")
            deps = test_case_gen.get("dependencies")

            project = APP_MODELS.Project.objects.get(id=int(job.project))
            provider_components = project.provider.get_components_by_type()

            comp_map = {}

            for key, value in comps.items():
                action = value["action"]

                if value.get("type") == "element_lookup":
                    new_c = provider_components.get(
                        action_name=action,
                        default_arguments__label="by",
                        default_arguments__value=value.get("locator_type"),
                    )
                else:
                    new_c = provider_components.get(action_name=action)
                serializer = serializers.CreateProjectComponentSerializer(
                    data={
                        "project_id": job.project,
                        "test_case_id": job.test_case,
                        "component_id": new_c.id,
                        "extra_data": {"position": {"x": 383.2, "y": 273}},
                    }
                )
                serializer.is_valid(raise_exception=True)
                saved = serializer.save()
                project_component: APP_MODELS.ProjectComponent = saved["component"]

                if value.get("name"):
                    project_component.name = value["name"]
                    project_component.save(update_fields=["name"])

                if value.get('type') == 'navigation':
                    extra_kwargs = project_component.extra_arguments.first()
                    extra_kwargs.value = value['url']
                    extra_kwargs.save(update_fields=['value'])

                elif value.get('type') == "element_lookup":
                    extra_kwargs = project_component.extra_arguments.first()
                    extra_kwargs.value = value['locator']
                    extra_kwargs.save(update_fields=['value'])

                elif value.get('type') == "input_action":
                    extra_kwargs = project_component.extra_arguments.first()
                    extra_kwargs.value = value['value']
                    extra_kwargs.save(update_fields=['value'])

                comp_map[key] = project_component
                
            for dep in deps:
                source_key = dep["from"]
                target_key = dep["to"]

                source_comp = comp_map.get(source_key)
                target_comp = comp_map.get(target_key)

                if source_comp and target_comp:
                    APP_MODELS.ComponentDependency.objects.create(
                        source_component=source_comp,
                        target_component=target_comp,
                        dependency_type=dep.get("type", "DEPENDENCY"),
                        metadata={},
                    )

from django.db import models
from no_code_testing_app_server.shared import BaseModel
from app_user_auth import models as authModels
from workflow_builder_config_app.models import ComponentType
from runner_agent import models as RUNNER_AGENT_MODELS
from django.db import transaction


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
        authModels.TenantUser, on_delete=models.DO_NOTHING, related_name='app_user', null=True, blank=True)
    first_name = models.CharField(max_length=255, null=True, blank=False)
    last_name = models.CharField(max_length=255, null=True, blank=False)
    profession = models.CharField(max_length=255, null=True, blank=False)
    role = models.ForeignKey(
        OrgRole, on_delete=models.CASCADE, related_name="role_org_member")

    def delete(self, *args, **kwargs):
        try:
            deleting = super().delete(*args, **kwargs)
            if self.user:
                authModels.TenantUser.objects.delete_user(self.user)
            else:
                print("No associated TenantUser found.")
            return deleting
        except Exception as e:
            print(f"Error deleting TenantUser: {e}")


class Status(models.TextChoices):
    INDREAMSCAPE = 'In Dreamscape ✨'
    LAUNCHPREP = 'Launch Preparation 🚀'
    GALACTICCRUISE = 'Galactic Cruise ☄️'
    ORBITALPAUSE = 'Orbital Pause ⏸️'
    STELLARFINALE = 'Stellar Finale 🌟'
    CRASHLANDING = 'Crash Landing 💥'
    LOSTINVOID = 'Lost in Void 🕳️'


class Project(BaseModel):

    name = models.CharField(max_length=255, blank=False, null=True)
    description = models.TextField(blank=False, null=True)
    members = models.ManyToManyField(
        User, related_name="user_projects", blank=True)
    provider = models.ForeignKey(
        'workflow_builder_config_app.Provider',
        related_name="provider_projects", on_delete=models.SET_NULL, null=True, blank=True)
    managed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="managed_projects")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.INDREAMSCAPE,
        blank=False,
        null=False
    )

    selected_agent = models.ForeignKey(
        RUNNER_AGENT_MODELS.RunnerAgent, on_delete=models.SET_NULL, null=True, blank=True, related_name="runner_projects")

    def __str__(self):
        return f"{self.name} ({self.status})"

    def set_status(self, new_status, failure_reason=None):

        if new_status not in self.Status.values:
            raise ValueError(f"Invalid status: {new_status}")

        old_status = self.status
        self.status = new_status
        self.save()

        ProjectStatusLog.objects.create(
            project=self,
            old_status=old_status,
            new_status=new_status,
            failure_reason=failure_reason if new_status == Status.CRASHLANDING else None
        )


class ProjectTestFlow(BaseModel):
    name = models.CharField(max_length=255, null=False, blank=False)
    project = models.ForeignKey(
        Project, related_name="test_flows", on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class ProjectTestCase(BaseModel):
    """like provider component"""
    name = models.CharField(max_length=255, null=False, blank=False)
    project = models.ForeignKey(
        Project, related_name="test_case_flows", on_delete=models.CASCADE)
    is_reference = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class TestFlowComponent(ProjectTestCase):
    """like project component"""
    builder_config = models.JSONField(null=True, blank=True, default=None)
    test_flow = models.ForeignKey(
        ProjectTestFlow, related_name="test_flow_components", on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.name

    @classmethod
    def clone_from_test_case(cls, test_case, test_flow, extra_data=None):
        with transaction.atomic():

            flow_test_case = cls(
                name=test_case.name,
                builder_config=extra_data,
                test_flow=test_flow,
                is_reference=False,  # to change false
                project=test_case.project
            )
            flow_test_case.save()
            project_components = ProjectComponent.objects.filter(
                project_test_case=test_case)

            component_mapping = {}
            for project_component in project_components:
                new_component = ProjectComponent(
                    name=project_component.name,
                    action_name=project_component.action_name,
                    module=project_component.module,
                    initial_config=project_component.initial_config,
                    extra_download_assets=project_component.extra_download_assets,
                    is_function=project_component.is_function,
                    is_default=project_component.is_default,
                    type=project_component.type,
                    project=project_component.project,
                    project_test_case=flow_test_case,
                    builder_config=project_component.builder_config,
                )
                new_component.save()
                try:
                    new_extra_args = []
                    for kwarg in project_component.extra_arguments.all():
                        new_kwarg = Kwarg(
                            label=kwarg.label,
                            value=kwarg.value,
                        )
                        new_kwarg.save()
                        new_extra_args.append(new_kwarg)
                    if new_extra_args:
                        new_component.extra_arguments.set(new_extra_args)
                except Exception as e:
                    raise ValueError(
                        f"Failed to clone extra_arguments for component {project_component.name}: {str(e)}")
                try:
                    new_default_args = []
                    for kwarg in project_component.default_arguments.all():
                        new_kwarg = Kwarg(
                            label=kwarg.label,
                            value=kwarg.value,
                        )
                        new_kwarg.save()
                        new_default_args.append(new_kwarg)
                    if new_default_args:
                        new_component.default_arguments.set(new_default_args)
                except Exception as e:
                    raise ValueError(
                        f"Failed to clone extra_arguments for component {project_component.name}: {str(e)}")
                # new_component.default_arguments.set(
                #     project_component.default_arguments.all())

                component_mapping[project_component.id] = new_component

            dependencies = ComponentDependency.objects.filter(
                source_component__in=project_components,
                target_component__in=project_components
            )
            for dependency in dependencies:
                new_dependency = ComponentDependency(
                    source_component=component_mapping[dependency.source_component.id],
                    target_component=component_mapping[dependency.target_component.id],
                    dependency_type=dependency.dependency_type,
                    metadata=dependency.metadata
                )
                new_dependency.save()

            return flow_test_case


class TestFlowDependency(models.Model):
    source_component = models.ForeignKey(
        TestFlowComponent,
        on_delete=models.CASCADE,
        related_name="outgoing_test_flow_dependencies",
    )
    target_component = models.ForeignKey(
        TestFlowComponent,
        on_delete=models.CASCADE,
        related_name="incoming_test_flow_dependencies",
    )

    class Meta:
        unique_together = ['source_component',
                           'target_component']
        verbose_name = "TestFlows Dependency"
        verbose_name_plural = "TestFlows Dependencies"

    def __str__(self):
        return f"{self.source_component} -> {self.target_component}"


class ProjectTestFlowAtomicCases(BaseModel):
    name = models.CharField(max_length=255, null=False, blank=False)
    project = models.ForeignKey(
        Project, related_name="test_atomic_flows", on_delete=models.CASCADE)
    test_cases = models.ManyToManyField(ProjectTestCase, blank=True)

    def __str__(self):
        return self.name


class ProjectStatusLog(BaseModel):
    project = models.ForeignKey(
        Project, related_name="status_logs", on_delete=models.CASCADE)
    old_status = models.CharField(
        max_length=20, choices=Status.choices, null=True, blank=True)
    new_status = models.CharField(
        max_length=20, choices=Status.choices)
    failure_reason = models.TextField(null=True, blank=True)
    workflow = models.JSONField(null=True, blank=True)
    is_running = models.BooleanField(default=False)
    is_finish = models.BooleanField(default=False)
    is_failed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.project.name}"


class Kwarg(BaseModel):
    label = models.CharField(max_length=255, null=False, blank=False)
    value = models.CharField(max_length=255, null=True, blank=True, default="")

    def __str__(self):
        return self.label if self.value is None else self.label + " - " + self.value


class ProjectComponent(BaseModel):
    name = models.CharField(max_length=255, null=False, blank=False)
    action_name = models.CharField(max_length=255, null=False, blank=False)
    module = models.CharField(max_length=255, null=True, blank=True)
    initial_config = models.JSONField(null=True, blank=True)
    extra_download_assets = models.TextField(blank=True, null=True)
    is_function = models.BooleanField(default=False)
    is_default = models.BooleanField(default=False)
    extra_arguments = models.ManyToManyField(
        Kwarg, related_name="project_component_extra_arguments_kwargs",  blank=True)
    default_arguments = models.ManyToManyField(
        Kwarg, related_name="project_component_default_arguments_kwargs", blank=True)
    type = models.CharField(
        max_length=50,
        choices=ComponentType.choices,
        default=ComponentType.INPUT,
        null=False,
        blank=False
    )
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, null=True, blank=True)
    project_test_case = models.ForeignKey(
        ProjectTestCase, on_delete=models.CASCADE, null=True, blank=True)
    builder_config = models.JSONField(null=True, blank=True, default=None)

    def __str__(self):
        return self.name + " - " + self.action_name + " - "+self.project_test_case.name


class DependencyType(models.TextChoices):
    DEPENDENCY = "DEPENDENCY"
    RUN_AFTER = "RUN_AFTER"


class ComponentDependency(models.Model):
    source_component = models.ForeignKey(
        ProjectComponent,
        on_delete=models.CASCADE,
        related_name="outgoing_dependencies",
    )
    target_component = models.ForeignKey(
        ProjectComponent,
        on_delete=models.CASCADE,
        related_name="incoming_dependencies",
    )
    dependency_type = models.CharField(
        max_length=50,
        choices=DependencyType.choices,
        default=DependencyType.DEPENDENCY.value,
    )
    metadata = models.JSONField(
        null=True,
        blank=True,
    )

    class Meta:
        unique_together = ['source_component',
                           'target_component', 'dependency_type']
        verbose_name = "Component Dependency"
        verbose_name_plural = "Component Dependencies"

    def __str__(self):
        return f"{self.source_component} -> {self.target_component} ({self.dependency_type})"

from runner_agent.models import RunnerAgent
from collections import defaultdict
from toposort import toposort_flatten
import logging
from app_backend import models
from rest_framework import serializers
from workflow_builder_config_app import serializers as WORKFLOW_CONFIG_SERIALIZERS
from no_code_testing_app_server.shared import DynamicModelSerializer
from app_user_auth.export_serializer import BaseTenantUserSerializer
from app_user_auth.models import TenantUser
from workflow_builder_config_app.models import Component
from copy import deepcopy

logger = logging.getLogger('no_code_testing_app')


class AppPermissionSerializer(DynamicModelSerializer):
    class Meta:
        model = models.AppPermission
        fields = '__all__'


class OrgRoleReadSerializer(DynamicModelSerializer):
    permissions = AppPermissionSerializer(many=True)

    class Meta:
        model = models.OrgRole
        fields = '__all__'


class OrgRoleCreateSerializer(DynamicModelSerializer):
    class Meta:
        model = models.OrgRole
        fields = '__all__'


class BaseOrgRoleSerializer(DynamicModelSerializer):
    class Meta:
        model = models.OrgRole
        exclude = ['permissions', 'can_delete']

    def get_fields(self):
        fields = super().get_fields()
        exclude_fields = self.context.get("exclude_fields", [])
        for field in exclude_fields:
            fields.pop(field, default=None)

        return fields


class AppBaseUserSerializer(DynamicModelSerializer):

    class Meta:
        model = models.User
        fields = '__all__'

    def get_fields(self):
        fields = super().get_fields()
        exclude_fields = self.context.get("exclude_fields", [])
        for field in exclude_fields:
            fields.pop(field, default=None)
        return fields


class AppUserSerializer(serializers.ModelSerializer):
    role = BaseOrgRoleSerializer()
    user = BaseTenantUserSerializer()

    class Meta:
        model = models.User
        fields = '__all__'

    def get_fields(self):
        fields = super().get_fields()
        exclude_fields = self.context.get("exclude_fields", [])
        for field in exclude_fields:
            fields.pop(field, default=None)
        return fields

    def to_representation(self, instance):
        data = super().to_representation(instance)
        tenant = data.pop('user', {})
        tenant.pop('id', '')
        data.update(tenant)
        return data


class CreateUpdateUserSerializer(serializers.ModelSerializer):
    user = BaseTenantUserSerializer()

    class Meta:
        model = models.User
        fields = '__all__'

    def __init__(self, instance=None, data=..., **kwargs):
        super().__init__(instance, data, **kwargs)

    def create(self, validated_data):
        try:
            tenant_user_data = validated_data.pop('user')
            tenant = self.context.get('request').tenant
            tenant_user_created = TenantUser.objects.create(**tenant_user_data)
            tenant_user_created.tenants.add(tenant)
            app_user = models.User.objects.create(
                **validated_data, user=tenant_user_created)
            return app_user
        except Exception as e:
            logger.exception(f"Error creating user: {str(e)}")
            raise serializers.ValidationError({"detail": str(e)})

    def update(self, instance, validated_data):
        try:
            tenant_user_data = validated_data.pop('user', None)
            if tenant_user_data:
                tenant_user_serializer = BaseTenantUserSerializer(
                    instance.user, data=tenant_user_data, partial=True
                )
                tenant_user_serializer.is_valid(raise_exception=True)
                tenant_user_serializer.save()

            return super().update(instance, validated_data)
        except Exception as e:
            logger.exception(f"Error updating user: {str(e)}")
            raise e


class ProjectSerializer(DynamicModelSerializer):
    provider = WORKFLOW_CONFIG_SERIALIZERS.BaseProviderSerializer()
    managed_by = AppUserSerializer()
    members = AppUserSerializer(many=True)

    class Meta:
        model = models.Project
        fields = '__all__'


class ProjectStatusLogSerializer(DynamicModelSerializer):
    workflow = serializers.JSONField(read_only=True)
    agent_key = serializers.SerializerMethodField("get_agent")
    project = ProjectSerializer()

    class Meta:
        model = models.ProjectStatusLog
        fields = '__all__'

    def get_agent(self, obj: models.ProjectStatusLog):
        return str(obj.project.selected_agent.agent_key)


class CreateProjectSerializer(DynamicModelSerializer):

    class Meta:
        model = models.Project
        fields = '__all__'

    def create(self, validated_data):
        project = super().create(validated_data)
        workflow = models.ProjectTestFlow(project=project, name="Test flow 1")
        workflow.save()
        return project


class ProjectTestFlowSerializer(DynamicModelSerializer):

    class Meta:
        model = models.ProjectTestFlow
        fields = '__all__'


class ProjectTestCaseSerializer(DynamicModelSerializer):

    class Meta:
        model = models.ProjectTestCase
        fields = '__all__'


class ProjectTestCaseSerializer(DynamicModelSerializer):

    class Meta:
        model = models.ProjectTestCase
        fields = '__all__'


class KwargSerializer(DynamicModelSerializer):

    class Meta:
        model = models.Kwarg
        fields = '__all__'
        ref_name = "AppBackendKwargSerializer"


class ProjectComponentSerializer(DynamicModelSerializer):
    extra_arguments = KwargSerializer(many=True)
    default_arguments = KwargSerializer(many=True, read_only=True)

    class Meta:
        model = models.ProjectComponent
        fields = '__all__'

    def update(self, instance, validated_data):
        extra_arguments_data = validated_data.pop('extra_arguments', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if extra_arguments_data is not None:
            current_kwarg_ids = set(
                instance.extra_arguments.values_list('id', flat=True))
            new_kwarg_ids = set(
                item.get('id') for item in extra_arguments_data if item.get('id')
            )

            for kwarg_id in current_kwarg_ids - new_kwarg_ids:
                instance.extra_arguments.remove(
                    models.Kwarg.objects.get(id=kwarg_id))

            for kwarg_data in extra_arguments_data:
                kwarg_id = kwarg_data.get('id')
                if kwarg_id:
                    try:
                        kwarg = models.Kwarg.objects.get(id=kwarg_id)
                        KwargSerializer().update(kwarg, kwarg_data)
                        instance.extra_arguments.add(kwarg)
                    except models.Kwarg.DoesNotExist:
                        raise serializers.ValidationError(
                            f"Kwarg with id {kwarg_id} does not exist."
                        )
                else:
                    kwarg = models.Kwarg.objects.create(**kwarg_data)
                    instance.extra_arguments.add(kwarg)

        return instance


class CreateProjectComponentSerializer(serializers.Serializer):
    project_id = serializers.PrimaryKeyRelatedField(
        queryset=models.Project.objects.all(), source='project', write_only=True
    )
    component_id = serializers.PrimaryKeyRelatedField(
        queryset=Component.objects.all(), source='component', write_only=True
    )
    test_case_id = serializers.PrimaryKeyRelatedField(
        queryset=models.ProjectTestCase.objects.all(), source='projecttestcase', write_only=True
    )
    extra_data = serializers.JSONField(
        write_only=True
    )
    component = ProjectComponentSerializer(read_only=True)

    class Meta:
        fields = ('project_id', 'component_id', 'project', 'component')

    def create(self, validated_data):
        project = validated_data['project']
        component = validated_data['component']
        test_case = validated_data['projecttestcase']

        project_component = models.ProjectComponent(
            name=component.name,
            action_name=component.action_name,
            module=component.module,
            initial_config=deepcopy(
                component.initial_config) if component.initial_config else None,
            extra_download_assets=component.extra_download_assets,
            is_function=component.is_function,
            is_default=component.is_default,
            type=component.type,
            project=project,
            project_test_case=test_case,
            builder_config=validated_data['extra_data']
        )
        project_component.save()

        if component.extra_arguments.exists():
            cloned_extra_kwargs = [
                models.Kwarg(label=kwarg.label, value=kwarg.value)
                for kwarg in component.extra_arguments.all()
            ]
            models.Kwarg.objects.bulk_create(cloned_extra_kwargs)
            project_component.extra_arguments.set(cloned_extra_kwargs)

        if component.default_arguments.exists():
            cloned_default_kwargs = [
                models.Kwarg(label=kwarg.label, value=kwarg.value)
                for kwarg in component.default_arguments.all()
            ]
            models.Kwarg.objects.bulk_create(cloned_default_kwargs)
            project_component.default_arguments.set(cloned_default_kwargs)

        project_component.save()

        return {
            'component': project_component
        }


class ComponentDependencySerializer(serializers.ModelSerializer):

    class Meta:
        model = models.ComponentDependency
        fields = '__all__'


class EdgeSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.ComponentDependency
        fields = '__all__'


class ProjectComponentExecutionSerializer(serializers.Serializer):
    project_id = serializers.IntegerField()
    components = serializers.SerializerMethodField()
    execution_order = serializers.SerializerMethodField()
    dependencies = serializers.SerializerMethodField()

    def get_components(self, obj):
        project_id = obj['project_id']
        components = models.ProjectComponent.objects.filter(
            project_id=project_id)
        return ProjectComponentSerializer(components, many=True).data

    def get_dependencies(self, obj):
        project_id = obj['project_id']
        dependencies = models.ComponentDependency.objects.filter(
            source_component__project_id=project_id
        )
        return ComponentDependencySerializer(dependencies, many=True).data

    def get_execution_order(self, obj):
        project_id = obj['project_id']
        components = models.ProjectComponent.objects.filter(
            project_id=project_id)
        graph = defaultdict(set)
        component_ids = set()
        for component in components:
            component_ids.add(component.id)
            for dep in component.outgoing_dependencies.filter(dependency_type=models.DependencyType.RUN_AFTER):
                if dep.target_component.project_id == project_id:
                    graph[component.id].add(dep.target_component.id)

        try:
            ordered_ids = toposort_flatten(graph)
            ordered_ids = [cid for cid in ordered_ids if cid in component_ids]
            id_to_name = {c.id: c.name for c in components}
            return [{'id': cid, 'name': id_to_name.get(cid, 'Unknown')} for cid in ordered_ids]
        except ValueError:
            raise serializers.ValidationError(
                "Circular RUN_AFTER dependencies detected.")

    def validate(self, data):
        project_id = data['project_id']
        if not models.ProjectComponent.objects.filter(project_id=project_id).exists():
            raise serializers.ValidationError(
                f"No components found for project_id {project_id}")
        return data

    def to_representation(self, instance):
        data = super().to_representation(instance)
        components = data['components']
        execution_order = data['execution_order']
        dependencies = data['dependencies']

        component_dict = {comp['id']: comp for comp in components}

        for comp in components:
            comp['depends_on'] = [
                dep['source_component_id']
                for dep in dependencies
                if dep.get('target_component_id') == comp['id'] and dep['dependency_type'] == models.DependencyType.DEPENDENCY.value
            ]
            comp['run_after'] = [
                dep['source_component_id']
                for dep in dependencies
                if dep.get('target_component_id') == comp['id'] and dep['dependency_type'] == models.DependencyType.RUN_AFTER.value
            ]

        if any('target_component_id' not in dep for dep in dependencies):
            print(
                "Warning: Some dependencies missing 'target_component_id':", dependencies)
        return {
            'project_id': instance['project_id'],
            'components': component_dict,
            'execution_order': execution_order,
            'dependencies': dependencies
        }


class ExecuteProjectSerializer(serializers.Serializer):
    runner_id = serializers.PrimaryKeyRelatedField(
        queryset=RunnerAgent.objects.all(), source='runneragent', write_only=True
    )

    class Meta:
        fields = ('runner_id',)

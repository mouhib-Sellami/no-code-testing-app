from collections import defaultdict, deque
from django.core.exceptions import ValidationError
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


class TestFlowComponentSerializer(DynamicModelSerializer):

    class Meta:
        model = models.TestFlowComponent
        fields = '__all__'


class CreateTestFlowComponentSerializer(serializers.Serializer):
    flow_id = serializers.PrimaryKeyRelatedField(
        queryset=models.ProjectTestFlow.objects.all(), source='flow', write_only=True
    )
    test_case_id = serializers.PrimaryKeyRelatedField(
        queryset=models.ProjectTestCase.objects.all(), source='testcase', write_only=True
    )
    extra_data = serializers.JSONField(
        write_only=True
    )
    component = TestFlowComponentSerializer(read_only=True)

    class Meta:
        fields = ('flow_id', 'test_case_id', 'component')

    def create(self, validated_data):
        flow = validated_data['flow']
        test_case = validated_data['testcase']
        print("*"*10)
        new_flow_component = models.TestFlowComponent.clone_from_test_case(
            test_case=test_case,
            test_flow=flow,
            extra_data=validated_data['extra_data']
        )
        return {
            'component': new_flow_component
        }


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


class TestFlowEdgeSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.TestFlowDependency
        fields = '__all__'


# class ProjectComponentExecutionSerializer(serializers.Serializer):
#     project_id = serializers.IntegerField()
#     components = serializers.SerializerMethodField()
#     execution_order = serializers.SerializerMethodField()
#     dependencies = serializers.SerializerMethodField()

#     def get_components(self, obj):
#         project_id = obj['project_id']
#         components = models.ProjectComponent.objects.filter(
#             project_id=project_id)
#         return ProjectComponentSerializer(components, many=True).data

#     def get_dependencies(self, obj):
#         project_id = obj['project_id']
#         dependencies = models.ComponentDependency.objects.filter(
#             source_component__project_id=project_id
#         )
#         return ComponentDependencySerializer(dependencies, many=True).data

#     def get_execution_order(self, obj):
#         project_id = obj['project_id']
#         components = models.ProjectComponent.objects.filter(
#             project_id=project_id)
#         graph = defaultdict(set)
#         component_ids = set()
#         for component in components:
#             component_ids.add(component.id)
#             for dep in component.outgoing_dependencies.filter(dependency_type=models.DependencyType.RUN_AFTER):
#                 if dep.target_component.project_id == project_id:
#                     graph[component.id].add(dep.target_component.id)

#         try:
#             ordered_ids = toposort_flatten(graph)
#             ordered_ids = [cid for cid in ordered_ids if cid in component_ids]
#             id_to_name = {c.id: c.name for c in components}
#             return [{'id': cid, 'name': id_to_name.get(cid, 'Unknown')} for cid in ordered_ids]
#         except ValueError:
#             raise serializers.ValidationError(
#                 "Circular RUN_AFTER dependencies detected.")

#     def validate(self, data):
#         project_id = data['project_id']
#         if not models.ProjectComponent.objects.filter(project_id=project_id).exists():
#             raise serializers.ValidationError(
#                 f"No components found for project_id {project_id}")
#         return data

#     def to_representation(self, instance):
#         data = super().to_representation(instance)
#         components = data['components']
#         execution_order = data['execution_order']
#         dependencies = data['dependencies']

#         component_dict = {comp['id']: comp for comp in components}

#         for comp in components:
#             comp['depends_on'] = [
#                 dep['source_component_id']
#                 for dep in dependencies
#                 if dep.get('target_component_id') == comp['id'] and dep['dependency_type'] == models.DependencyType.DEPENDENCY.value
#             ]
#             comp['run_after'] = [
#                 dep['source_component_id']
#                 for dep in dependencies
#                 if dep.get('target_component_id') == comp['id'] and dep['dependency_type'] == models.DependencyType.RUN_AFTER.value
#             ]

#         if any('target_component_id' not in dep for dep in dependencies):
#             print(
#                 "Warning: Some dependencies missing 'target_component_id':", dependencies)
#         return {
#             'project_id': instance['project_id'],
#             'components': component_dict,
#             'execution_order': execution_order,
#             'dependencies': dependencies
#         }


class TestCaseExecutionSerializer(serializers.Serializer):
    test_case_id = serializers.IntegerField()
    components = serializers.SerializerMethodField()
    execution_order = serializers.SerializerMethodField()
    dependencies = serializers.SerializerMethodField()

    def get_components(self, obj):
        test_case_id = obj['test_case_id']
        components = models.ProjectComponent.objects.filter(
            project_test_case_id=test_case_id)
        return ProjectComponentSerializer(components, many=True).data

    def get_dependencies(self, obj):
        test_case_id = obj['test_case_id']
        dependencies = models.ComponentDependency.objects.filter(
            source_component__project_test_case__id=test_case_id
        )
        return ComponentDependencySerializer(dependencies, many=True).data

    def get_execution_order(self, obj):
        test_case_id = obj['test_case_id']
        components = models.ProjectComponent.objects.filter(
            project_test_case_id=test_case_id)
        graph = defaultdict(set)
        component_ids = set()
        for component in components:
            component_ids.add(component.id)
            for dep in component.outgoing_dependencies.filter(dependency_type=models.DependencyType.RUN_AFTER):
                if dep.target_component.project_test_case_id == test_case_id:
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
        test_case_id = data['test_case_id']
        if not models.ProjectComponent.objects.filter(project_test_case_id=test_case_id).exists():
            raise serializers.ValidationError(
                f"No components found for test_case_id {test_case_id}")
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
            logger.warning(
                "Some dependencies missing 'target_component_id': %s", dependencies)

        return {
            'test_case_id': instance['test_case_id'],
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

# class ProjectTestFlowExecutionSerializer(serializers.Serializer):
#     test_flow_id = serializers.IntegerField()
#     project_id = serializers.SerializerMethodField()
#     components = serializers.SerializerMethodField()
#     execution_order = serializers.SerializerMethodField()
#     dependencies = serializers.SerializerMethodField()

#     def get_project_id(self, obj):
#         test_flow = models.ProjectTestFlow.objects.get(id=obj['test_flow_id'])
#         return test_flow.project.id

#     def get_components(self, obj):
#         test_flow_id = obj['test_flow_id']
#         test_flow_components = models.TestFlowComponent.objects.filter(
#             test_flow_id=test_flow_id)
#         project_components = models.ProjectComponent.objects.filter(
#             project_test_case__in=test_flow_components)
#         return ProjectComponentSerializer(project_components, many=True).data

#     def get_dependencies(self, obj):
#         test_flow_id = obj['test_flow_id']
#         test_flow_components = models.TestFlowComponent.objects.filter(
#             test_flow_id=test_flow_id)
#         project_components = models.ProjectComponent.objects.filter(
#             project_test_case__in=test_flow_components)

#         component_dependencies = models.ComponentDependency.objects.filter(
#             source_component__in=project_components,
#             target_component__in=project_components
#         )
#         component_dep_data = ComponentDependencySerializer(
#             component_dependencies, many=True).data

#         test_flow_dependencies = models.TestFlowDependency.objects.filter(
#             source_component__in=test_flow_components,
#             target_component__in=test_flow_components
#         )
#         component_id_map = {
#             tfc.id: tfc.project_test_case.id for tfc in test_flow_components if tfc.project_test_case}

#         test_flow_dep_data = []
#         for dep in test_flow_dependencies:
#             source_component_id = component_id_map.get(dep.source_component_id)
#             target_component_id = component_id_map.get(dep.target_component_id)
#             if source_component_id and target_component_id:
#                 test_flow_dep_data.append({
#                     'source_component_id': source_component_id,
#                     'target_component_id': target_component_id,
#                     'dependency_type': models.DependencyType.DEPENDENCY.value
#                     'metadata': None
#                 })

#         return component_dep_data + test_flow_dep_data

#     def get_execution_order(self, obj):
#         test_flow_id = obj['test_flow_id']
#         test_flow_components = models.TestFlowComponent.objects.filter(
#             test_flow_id=test_flow_id)
#         project_components = models.ProjectComponent.objects.filter(
#             project_test_case__in=test_flow_components)

#         graph = defaultdict(set)
#         component_ids = set()
#         component_id_map = {
#             tfc.id: tfc.project_test_case.id for tfc in test_flow_components if tfc.project_test_case}

#         for component in project_components:
#             component_ids.add(component.id)
#             for dep in component.outgoing_dependencies.filter(
#                 dependency_type=models.DependencyType.RUN_AFTER,
#                 target_component__in=project_components
#             ):
#                 graph[component.id].add(dep.target_component.id)

#         test_flow_dependencies = models.TestFlowDependency.objects.filter(
#             source_component__in=test_flow_components,
#             target_component__in=test_flow_components
#         )
#         for dep in test_flow_dependencies:
#             source_id = component_id_map.get(dep.source_component_id)
#             target_id = component_id_map.get(dep.target_component_id)
#             if source_id and target_id:
#                 graph[source_id].add(target_id)

#         try:
#             ordered_ids = toposort_flatten(graph)
#             ordered_ids = [cid for cid in ordered_ids if cid in component_ids]
#             id_to_name = {c.id: c.name for c in project_components}
#             return [{'id': cid, 'name': id_to_name.get(cid, 'Unknown')} for cid in ordered_ids]
#         except ValueError:
#             raise serializers.ValidationError(
#                 f"Circular RUN_AFTER dependencies detected in test flow {test_flow_id}."
#             )

#     def validate(self, data):
#         test_flow_id = data['test_flow_id']
#         if not models.ProjectTestFlow.objects.filter(id=test_flow_id).exists():
#             raise serializers.ValidationError(
#                 f"No test flow found for test_flow_id {test_flow_id}"
#             )
#         if not models.TestFlowComponent.objects.filter(test_flow_id=test_flow_id).exists():
#             raise serializers.ValidationError(
#                 f"No components found for test_flow_id {test_flow_id}"
#             )
#         return data

#     def to_representation(self, instance):
#         data = super().to_representation(instance)
#         components = data['components']
#         execution_order = data['execution_order']
#         dependencies = data['dependencies']

#         component_dict = {comp['id']: comp for comp in components}

#         for comp in components:
#             comp['depends_on'] = [
#                 dep['source_component_id']
#                 for dep in dependencies
#                 if dep.get('target_component_id') == comp['id'] and dep['dependency_type'] == models.DependencyType.DEPENDENCY.value
#             ]
#             comp['run_after'] = [
#                 dep['source_component_id']
#                 for dep in dependencies
#                 if dep.get('target_component_id') == comp['id'] and dep['dependency_type'] == models.DependencyType.RUN_AFTER.value
#             ]

#         if any('target_component_id' not in dep for dep in dependencies):
#             print(
#                 "Warning: Some dependencies missing 'target_component_id':", dependencies)

#         return {
#             'project_id': data['project_id'],
#             'test_flow_id': instance['test_flow_id'],
#             'components': component_dict,
#             'execution_order': execution_order,
#             'dependencies': dependencies
#         }


class TestFlowExecutionComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TestFlowComponent
        fields = "__all__"

    @staticmethod
    def get_execution_order(test_flow):
        components = models.TestFlowComponent.objects.filter(
            test_flow=test_flow)
        component_ids = set(components.values_list('id', flat=True))

        graph = defaultdict(list)
        in_degree = defaultdict(int)

        for component in components:
            in_degree[component.id] = 0

        dependencies = models.TestFlowDependency.objects.filter(
            source_component__test_flow=test_flow,
            target_component__test_flow=test_flow
        )

        for dep in dependencies:
            source_id = dep.source_component_id
            target_id = dep.target_component_id
            graph[source_id].append(target_id)
            in_degree[target_id] += 1

        queue = deque()
        result = []

        for component_id in component_ids:
            if in_degree[component_id] == 0:
                queue.append(component_id)

        while queue:
            current_id = queue.popleft()
            result.append(current_id)

            for neighbor_id in graph[current_id]:
                in_degree[neighbor_id] -= 1
                if in_degree[neighbor_id] == 0:
                    queue.append(neighbor_id)

        if len(result) != len(component_ids):
            raise ValidationError(
                "Cycle detected in TestFlowComponent dependencies")

        id_to_component = {c.id: c for c in components}
        ordered_components = [id_to_component[cid] for cid in result]

        return ordered_components


class TestFlowExecutionSerializer(serializers.ModelSerializer):
    components = serializers.SerializerMethodField()

    class Meta:
        model = models.ProjectTestFlow
        fields = ['id', 'components']

    def get_components(self, obj):
        ordered_components = TestFlowExecutionComponentSerializer.get_execution_order(
            obj)
        serializer = TestFlowExecutionComponentSerializer(
            ordered_components, many=True)
        return serializer.data


class WorkflowTestCaseExecuterSerializer(serializers.Serializer):
    flow_case_id = serializers.PrimaryKeyRelatedField(
        queryset=models.ProjectTestFlow.objects.all(), source='flow', write_only=True
    )

    class Meta:
        fields = ['flows']

    def to_representation(self, instance):
        flows = TestFlowExecutionSerializer(
            instance['flow'])
        flows = flows.data
        test_flow = []
        for test_case in flows.get('components', []):
            execution = TestCaseExecutionSerializer(
                data={"test_case_id": test_case.get('id')})
            execution.is_valid(raise_exception=True)
            test_flow.append({
                "test_case": test_case,
                "workflow": execution.data
            })
        return {"flows": test_flow}

import logging
from app_backend import models
from rest_framework import serializers
from workflow_builder_config_app import serializers as WORKFLOW_CONFIG_SERIALIZERS
from no_code_testing_app_server.shared import DynamicModelSerializer
from app_user_auth.export_serializer import BaseTenantUserSerializer
from app_user_auth.models import TenantUser

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
        
class CreateProjectSerializer(DynamicModelSerializer):

    class Meta:
        model = models.Project
        fields = '__all__'

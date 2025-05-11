import logging
from app_backend import models
from rest_framework import serializers
from app_user_auth.models import TenantUser
from workflow_builder_config_app.viewsets import serializers as WORKFLOW_CONFIG_SERIALIZERS

logger = logging.getLogger('no_code_testing_app')


class BaseTenantUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenantUser
        fields = (
            'id',
            'username',
            'email',
            'is_verified',
            'is_active'
        )

    def validate(self, attrs):
        return attrs

    def validate_username(self, value):
        instance = getattr(self, 'instance', None)
        if instance and instance.username == value:
            return value
        if TenantUser.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                "A user with this username already exists.")
        return value

    def validate_email(self, value):
        instance = getattr(self, 'instance', None)
        if instance and instance.email == value:
            return value
        if TenantUser.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "A user with this email already exists.")
        return value


class AppPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AppPermission
        fields = '__all__'


class OrgRoleReadSerializer(serializers.ModelSerializer):
    permissions = AppPermissionSerializer(many=True)

    class Meta:
        model = models.OrgRole
        fields = '__all__'


class OrgRoleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.OrgRole
        fields = '__all__'


class BaseOrgRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.OrgRole
        exclude = ['permissions', 'can_delete']

    def get_fields(self):
        fields = super().get_fields()
        exclude_fields = self.context.get("exclude_fields", [])
        for field in exclude_fields:
            fields.pop(field, default=None)

        return fields


class AppBaseUserSerializer(serializers.ModelSerializer):

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


class ProjectSerializer(serializers.ModelSerializer):
    provider = WORKFLOW_CONFIG_SERIALIZERS.ProviderSerializer()
    managed_by = AppUserSerializer()
    members = AppUserSerializer(many=True)

    class Meta:
        model = models.Project
        fields = '__all__'

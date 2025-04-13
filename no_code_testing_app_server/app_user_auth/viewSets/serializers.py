import logging
from app_user_auth import models
from rest_framework import serializers
from app_backend import models as appModels
from django.contrib.auth import get_user_model
from django_tenants.utils import tenant_context
from app_tenant.viewSets import serializers as TenantSerializers
from app_backend.viewSets import serializers as AppBackendSerializer

logger = logging.getLogger('no_code_testing_app')


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    class Meta:
        fields = ('username', 'password',)


class UserSerializer(serializers.ModelSerializer):

    role = serializers.SerializerMethodField("get_user_role")
    organization = serializers.SerializerMethodField("get_user_organization")

    class Meta:
        model = models.TenantUser
        fields = (
            'role',
            'organization',
        )

    def get_user_role(self, obj):
        try:
            tenant = obj.tenants.all().first()
            with tenant_context(tenant):
                return AppBackendSerializer.OrgRoleReadSerializer(obj.app_user.role).data
        except Exception as e:
            logger.exception(str(e))
        return None

    def get_user_organization(self, obj):
        tenant = obj.tenants.all().first()
        if tenant:
            return TenantSerializers.TenantSerializer(tenant).data
        else:
            return None


class BaseUserSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField('get_tenant_user')

    class Meta:
        model = models.TenantUser
        fields = (
            'id',
            'username',
            'email',
            'user'
        )

    def get_tenant_user(self, obj):
        try:
            tenant = obj.tenants.all().first()
            with tenant_context(tenant):
                return AppBackendSerializer.AppBaseUserSerializer(obj.app_user).data
        except Exception as e:
            logger.exception(str(e))
        return None

    def to_representation(self, instance):
        data = super().to_representation(instance)

        user_data = data.pop('user', {}) or {}
        user_data.pop('role', {})
        user_data.pop('user', {})
        id = user_data.pop('id', {})
        data.update(user_data)
        data.update({'tenant_id': id})
        return data


class UserSignupViewSerializer(serializers.ModelSerializer):
    organization = TenantSerializers.OrganizationSignUpSerializer()

    class Meta:
        model = models.TenantUser
        fields = ('username', 'email', 'password', 'organization')
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate_username(self, value):
        User = get_user_model()
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                "A user with this username already exists.")
        return value

    def validate_email(self, value):
        User = get_user_model()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "A user with this email already exists.")
        return value

    def validate(self, data):
        if not data.get('organization'):
            raise serializers.ValidationError(
                {"organization": "This field is required."})
        return data

    def create(self, validated_data):
        org_data = validated_data.pop('organization')
        org_serializer = TenantSerializers.OrganizationSignUpSerializer(
            data=org_data)
        org_serializer.is_valid(raise_exception=True)
        tenant = org_serializer.save()
        User = get_user_model()
        user = User.objects.create(
            **validated_data
        )
        tenant.owner = user
        tenant.save(update_fields=['owner'])
        user.tenants.add(tenant)
        # tenant_organization: appModels.Organization = tenant
        try:
            with tenant_context(tenant):
                tenant_user: appModels.User = appModels.User()
                tenant_user.role = appModels.OrgRole.objects.filter(
                    name="Owner").first()
                tenant_user.user = user
                tenant_user.save()
        except Exception as e:
            logger.exception(str(e))
        return user

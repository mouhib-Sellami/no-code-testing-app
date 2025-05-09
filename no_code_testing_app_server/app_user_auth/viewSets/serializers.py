import logging
from app_user_auth import models
from rest_framework import serializers
from app_backend import models as appModels
from django.contrib.auth import get_user_model
from django_tenants.utils import tenant_context
from app_tenant.viewSets import serializers as TenantSerializers
from app_backend.viewSets import serializers as AppBackendSerializer
from django.core.validators import RegexValidator
from no_code_testing_app_server.utils import verify_token_expiration

logger = logging.getLogger('no_code_testing_app')


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    class Meta:
        fields = ('username', 'password',)


class UserSerializer(serializers.ModelSerializer):

    role = serializers.SerializerMethodField("get_user_role")
    organization = serializers.SerializerMethodField("get_user_organization")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        extra_fields = self.context.get('extra_fields', [])
        for field in extra_fields:
            if field not in self.fields:
                self.fields[field] = serializers.CharField(
                    read_only=True, default='')

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
    organization = serializers.SerializerMethodField("get_user_organization")

    class Meta:
        model = models.TenantUser
        fields = (
            'id',
            'username',
            'email',
            'user',
            'organization'
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        extra_fields = self.context.get('extra_fields', [])
        for field in extra_fields:
            if field not in self.fields:
                self.fields[field] = serializers.CharField(
                    read_only=True, default='')

        exclude_fields = self.context.get('exclude_fields', [])
        for field in exclude_fields:
            if field in self.fields:
                self.fields.pop(field)

    def get_tenant_user(self, obj):
        try:
            tenant = obj.tenants.all().first()
            with tenant_context(tenant):
                return AppBackendSerializer.AppBaseUserSerializer(obj.app_user).data
        except Exception as e:
            logger.exception(str(e))
        return None

    def get_user_organization(self, obj):
        tenant = obj.tenants.all().first()
        if tenant:
            return TenantSerializers.TenantSerializer(tenant).data
        else:
            return None

    def to_representation(self, instance):
        data = super().to_representation(instance)

        user_data = data.pop('user', {}) or {}
        user_data.pop('role', {})
        user_data.pop('user', {})
        id = user_data.pop('id', {})
        data.update(user_data)
        data.update({'tenant_user_id': id})
        return data


class UserSignupViewSerializer(serializers.ModelSerializer):
    organization = TenantSerializers.OrganizationSignUpSerializer()
    first_name = serializers.CharField()
    last_name = serializers.CharField()

    class Meta:
        model = models.TenantUser
        fields = ('username', 'email', 'first_name',
                  'last_name', 'password', 'organization')
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
        first_name = validated_data.pop('first_name')
        last_name = validated_data.pop('last_name')
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
        try:
            with tenant_context(tenant):
                tenant_user: appModels.User = appModels.User()
                tenant_user.role = appModels.OrgRole.objects.filter(
                    name="Owner").first()
                tenant_user.user = user
                tenant_user.first_name = first_name
                tenant_user.last_name = last_name
                tenant_user.save()
        except Exception as e:
            logger.exception(str(e))
        return user


class ForgetPasswordRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(validators=[
        RegexValidator(
            regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            message='Enter a valid email address.',
            code='invalid_email'
        )
    ])

    class Meta:
        fields = ('email',)


class PasswordResetSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=255, required=True)
    password = serializers.CharField(
        max_length=128, write_only=True, required=True)
    confirm_password = serializers.CharField(
        max_length=128, write_only=True, required=True)

    def validate(self, data):
        if data['password'] != data['confirm_password']:

            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match."})

        if verify_token_expiration(data['token']):
            raise serializers.ValidationError({"token": "Token is expired."})
        else:
            user = models.TenantUser.objects.filter(
                reset_token=data['token']).first()
            if user == None:
                raise serializers.ValidationError(
                    {"token": "Token is expired."})
            data['user'] = user
        return data

    def save(self):
        user = self.validated_data['user']
        password = self.validated_data['password']
        print(self.validated_data)
        user.set_password(password)
        user.reset_token = None
        user.save(update_fields=['password'])
        return user

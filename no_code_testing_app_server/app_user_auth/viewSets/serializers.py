from rest_framework import serializers
from app_user_auth import models
from app_tenant import serializers as TenantSerializers
from django.contrib.auth import get_user_model


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    class Meta:
        fields = ('username', 'password',)


class BaseUserSerializer(serializers.ModelSerializer):
    organization = serializers.SerializerMethodField('get_user_tenant')

    class Meta:
        model = models.TenantUser
        fields = (
            'id',
            'username',
            'is_active',
            'organization',
            'created_at'
        )

    def get_user_tenant(self, obj):
        tenant = obj.tenants.all().first()
        if tenant:
            return TenantSerializers.TenantSerializer(tenant).data
        else:
            return None


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
        return user

from rest_framework import serializers
from app_user_auth import models
from app_tenant import serializers as TenantSerializers


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    class Meta:
        fields = ('username', 'password',)


class UserSignUpSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    email = serializers.EmailField()

    class Meta:
        fields = ('username', 'password', 'email')


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

from rest_framework import serializers
from app_user_auth import models


class BaseTenantUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TenantUser
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
        if models.TenantUser.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                "A user with this username already exists.")
        return value

    def validate_email(self, value):
        instance = getattr(self, 'instance', None)
        if instance and instance.email == value:
            return value
        if models.TenantUser.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "A user with this email already exists.")
        return value

import logging
from app_backend import models
from rest_framework import serializers

logger = logging.getLogger('no_code_testing_app')


class ProjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Project
        fields = '__all__'


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
